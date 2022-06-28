from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponsePermanentRedirect
# from django.contrib.auth.models import User
from django.forms import ValidationError
from django.forms.models import model_to_dict
from django.contrib.auth import authenticate, login
from django.contrib import messages

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from datetime import datetime, timedelta, timezone

from django.core import mail
from django.core.mail import EmailMessage, EmailMultiAlternatives

from django import template

from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text, smart_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.views import View 
from account.tokens import account_activation_token

import jwt
import requests
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.translation import ugettext_lazy as _  # noqa: F401

from rest_framework import generics, status, views, permissions, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework.viewsets import GenericViewSet, ModelViewSet, ViewSet
from rest_framework import status

from collections import defaultdict
from rest_framework.settings import api_settings


from account.models import *

from .renderers import *
from .serializers import *

from simple_python_api import settings

from django.core.files.storage import FileSystemStorage



# Create your views here.

class CustomRedirect(HttpResponsePermanentRedirect):
    allowed_schemes = settings.REDIRECT_ALLOWED_SCHEMES
    

# ***

class RegisterView(generics.GenericAPIView):

    serializer_class = RegisterSerializer
    renderer_classes = (UserRenderer,)
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        user = request.data

        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        user_data = serializer.validated_data
        user = User.objects.get(email=user_data['email'])

        user.is_active = True
            
        user.save()
            
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class LoginAPIView(generics.GenericAPIView):

    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={"request": request})

        serializer.is_valid(raise_exception=True)
        login_data = serializer.validated_data

        current_site = get_current_site(request).domain

        relativeLink = "/api/openid/token"
        # relativeLink = "/openid/token"

        absurl = current_site + relativeLink
        
        if "http://" not in absurl:
            absurl = f"http://{current_site}{relativeLink}"
        
        input_request = {
            "username": login_data["username"],
            "password": login_data["password"],
            "client_id": login_data["client_id"],
            "client_secret": login_data["client_secret"],
            "grant_type": "password",
        }

        user = User.objects.get(username=login_data['username'])
        
        try:

            """
                client id : 252055

                client_secret : 6a10d8e2610e15cb70e27f09938cc3cee0cd03aa04c2f8d8f04509e3
                
            """

            if user.is_active:
                output = requests.post(absurl, data=input_request, timeout=20)

                res = output.json()

                print("\n")
                print("*************************** JSON Response Data in Post Login Api ****************************")
                print(res)
                print("\n")

                response = {"tokens": {
                    'access_token': res["access_token"],
                    'refresh_token': res["refresh_token"],
                    'expires_in': res["expires_in"],
                    'token_type': res["token_type"],
                    'id_token': res["id_token"],
                }}
                
                """
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "user_type": user.get_user_type_display(),
                    "password": password,
                    "client_id": client_id,
                    "client_secret": client_secret,
                """
                
                photo = ""
                
                response["first_name"] = user.first_name
                response["last_name"] = user.last_name
                response["user_type"] = user.get_user_type_display()
                
                if user.photo:
                    photo = user.photo.url
                    
                response["photo"] = photo

                response.update(serializer.data)

                return Response(response, status=status.HTTP_200_OK)

            return Response(
                {
                    "error": "User not active"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print('["ERROR"] >>>>>>>>>',e)
            
            return Response(
                {"error": _("Client authentication failed (e.g., unknown client,"
                            + " no client authentication included,"
                            + " or unsupported authentication method")},  # a traduire
                status=status.HTTP_400_BAD_REQUEST,
            )



# Eroor !!!!!   "error": "redirect_url not provided"  to fix 
class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = request.data.get('email', '')

        try:
            user_reset = User.objects.get(email=email)

            if not user_reset:
                return Response(
                    {
                        'error': _("User doesn't exist in the system")  # a traduire
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
                token = PasswordResetTokenGenerator().make_token(user)

                current_site = get_current_site(request=request).domain
                relativeLink = reverse(
                    # 'auth:password-reset-confirm',
                    # 'service:password-reset-confirm',
                    'password-reset-confirm',
                    kwargs={
                        'uidb64': uidb64,
                        'token': token
                    }
                )
                redirect_url = request.data.get('redirect_url', '')
                absurl = current_site + relativeLink  # a traduire
                """
                email_body = _('Hello, \n Use link below to reset your password  \n') + \
                    absurl + "?redirect_url=" + redirect_url
                data = {'email_body': email_body, 'to_email': user.email,
                        'email_subject': 'Reset your passsword'}
                EmailSender.send_email(data)

                """ 

                current_site = get_current_site(request)

                subject = 'Password Reset on ' + str(current_site.domain)

                html_message = _(
                        '<b>Hello</b>, \
                        <br><br>\n\n You\'re receiving this email because you requested a password reset. \
                        <br><br>\n\n Use the link below to reset your password <br> <br>\n') + \
                    absurl + "?redirect_url=" + redirect_url + '<br> <br> <br> <br> \
                        Your username, in case you\'ve forgotten: <b>' + str(user.username) + '</b>'

                plain_message = _('Hello, \n Use the link below to reset your password  \n') + \
                    absurl + "?redirect_url=" + redirect_url

                from_email = settings.EMAIL_HOST_USER
                to = user.email

                mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message)

            return Response(
                {
                    'success': _('We have sent you a link to reset your password')
                },  # a traduire
                status=status.HTTP_200_OK
            )

        except User.DoesNotExist:
            return Response(
                    {
                        'error': _("User doesn't exist in the system")  # a traduire
                    },
                    status=status.HTTP_400_BAD_REQUEST
            )


class PasswordTokenCheckAPI(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token):

        redirect_url = request.GET.get('redirect_url')

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                if len(redirect_url) > 3:
                    return CustomRedirect(redirect_url + '?token_valid=False')
                else:
                    return Response(
                        {
                            'error': _('redirect_url not provided')  # a traduire
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

            if redirect_url and len(redirect_url) > 3:
                return CustomRedirect(
                    redirect_url + '?token_valid=True&message=Credentials Valid&uidb64=' + uidb64 + '&token=' + token
                )
            else:
                return Response(
                    {
                        'error': _('redirect_url not provided')  # a traduire
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        except DjangoUnicodeDecodeError:
            try:
                if not PasswordResetTokenGenerator().check_token(user):
                    return CustomRedirect(redirect_url + '?token_valid=False')

            except UnboundLocalError:
                return Response(
                    {
                        'error': _('Token is not valid, please request a new one')  # a traduire
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )


class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {
                'success': True,
                'message': _('Password reset success')  # a traduire
            },
            status=status.HTTP_200_OK
        )

