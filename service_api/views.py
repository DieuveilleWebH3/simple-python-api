from time import sleep
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponsePermanentRedirect
# from django.contrib.auth.models import User
from django.forms import ValidationError
from django.forms.models import model_to_dict
from django.contrib.auth import authenticate, login
from django.contrib import messages
import re

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

        try:
            if 'username' in request.data:
                if User.objects.get(username=request.data['username']):
                    pass
        except User.DoesNotExist:
            return Response(
                {
                    "error": "User does not exist"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
             
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

            if user.is_active:
                output = requests.post(absurl, data=input_request, timeout=20)

                res = output.json()

                response = {"tokens": {
                    'access_token': res["access_token"],
                    'refresh_token': res["refresh_token"],
                    'expires_in': res["expires_in"],
                    'token_type': res["token_type"],
                    'id_token': res["id_token"],
                }}
                
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
            print('login error ["ERROR"] >>>>>>>>>',e)
            
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



# *******************************************************

# ********************************************** DONE *********************************************************
class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all().order_by('-created_at')
    # get_queryset = Category.objects.all().order_by('-created_at')

    lookup_field = "slug"

    def get_serializer(self, data):
        return self.serializer_class(data=data)
    
    def perform_create(self, serializer):
        serializer.save()
    
    def get_list_of_category(self, category_objects):
        category_list = [] 
        
        try:
            for category in category_objects:
                
                articles = []

                article_of_category = Articles.objects.filter(category=category)
                
                if article_of_category:
                    articles = [{'id':d.id, 'author': {'id':d.author.id, 'username':d.author.username, 'user_type': d.author.get_user_type_display()}, 'title':d.title, 'slug': d.slug, 'read_by': d.read_by, 'liked_by': d.liked_by} for d in article_of_category]
                
                one_category = {
                    'id': category.id,
                    'title': category.title,
                    'slug': category.slug,
                    'description': category.description,
                    'articles': articles,
                    'created_at': category.created_at.timestamp(),
                    'modified_at': category.modified_at.timestamp()
                }

                category_list.append(one_category)

            return category_list
        except Exception as e:
            raise ValidationError(f'[ERR]: category error ==> {e}')

    slug = openapi.Parameter('slug', in_=openapi.IN_QUERY, description='category\'s slug', type=openapi.TYPE_STRING)

    @swagger_auto_schema(
        manual_parameters=[slug])

    def list(self, request, *args, **kwargs):
        slug = request.query_params.get('slug', None)
        category_list = []

        try:

            if slug:
                
                category = Category.objects.filter(slug=slug)
                # if category.exists():
                if category:
                    
                    category_list = self.get_list_of_category(category)

                    return HttpResponse(
                        json.dumps(category_list),
                        status=status.HTTP_200_OK,
                    )
            else:
                
                # works but is cached,so only sending old list / queryset .. => to change 
                # category_list = self.get_list_of_category(self.queryset) 
                
                # return methods which is not iterable, look into it, harder
                # category_list = self.get_list_of_category(self.get_queryset)  
                
                category_list = self.get_list_of_category(Category.objects.all().order_by('-created_at'))

            return HttpResponse(
                    json.dumps(category_list),
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            return Response(
                f'category not found => [ERR]: {e}',
                status=status.HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(
        request_body=CategorySerializer,
        responses = {
            '200' : 'HttpResponse status 201',
            '400': 'category has not been created',
        },
    )

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            # headers = self.get_success_headers(serializer.data)
            # return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(json.dumps({
                    # "message": 'category with this title already exists.' if 'unique' in str(e) else str(e),
                    "message": str(e),
                    "data": json.dumps(request.data)
                }), status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        request_body=CategorySerializer,
        responses = {
            '200' : 'HttpResponse status 200',
            '400': 'category has not been updated',
        },
    )

    def update(self, request, slug, *args, **kwargs):

        try:
            
            category = Category.objects.get(slug=slug)

            if category:
                
                serializer = CategorySerializer(category, data=request.data)
                # serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)

                serializer.save()

                # print("\n")
                # print("******************** Serializer category Put Method *********************")
                # print("\n")
                # print(serializer.data)

                return Response(serializer.data, status=status.HTTP_200_OK)
            
            else:
                return Response(json.dumps({
                    "message": "category with that slug does not exist",
                    "data": json.dumps(request.data)
                }), status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(json.dumps({
                    # "message": 'category with this title already exists.' if 'unique' in str(e) else str(e),
                    "message": str(e),
                    "data": json.dumps(request.data)
                }), status=status.HTTP_400_BAD_REQUEST)


# ********************************* DONE ************************************************
class ArticleViewSet(ModelViewSet):
    serializer_class = ArticleSerializer
    queryset = Articles.objects.all().order_by('-id')

    lookup_field = "slug"

    def get_serializer(self, data):
        return self.serializer_class(data=data)
    
    def perform_create(self, serializer):
        serializer.save()
    
    def get_list_of_articles(self, articles_objects):
        articles_list = [] 
        
        try:
            for article in articles_objects:
                
                categories = []

                category_of_article = article.category.all()
                
                if category_of_article :
                    categories = [{'id':c.id, 'title':c.title, 'slug': c.slug} for c in category_of_article]
                
                one_article = {
                    'id': article.id,
                    'author': {'id':article.author.id, 'username':article.author.username, 'user_type': article.author.get_user_type_display() },
                    'title': article.title,
                    'slug': article.slug, 
                    "content": article.content,
                    'photo': "" if not article.photo else article.photo.url,
                    'read_by': article.read_by, 
                    'liked_by': article.liked_by,
                    'categories': categories,
                    'created_at': article.created_at.timestamp(),
                    'modified_at': article.modified_at.timestamp()
                }

                articles_list.append(one_article)

            return articles_list
        except Exception as e:
            raise ValidationError(f'[ERR]: article error ==> {e}')

        
    slug = openapi.Parameter('slug', in_=openapi.IN_QUERY, description='article\'s slug', type=openapi.TYPE_STRING)
    
    user_id = openapi.Parameter('user_id', in_=openapi.IN_QUERY, description='user\'s id', type=openapi.TYPE_INTEGER)
    

    @swagger_auto_schema(
        manual_parameters=[slug, user_id])

    def list(self, request, *args, **kwargs):
        slug = request.query_params.get('slug', None)
        user_id = request.query_params.get('user_id', None)
        
        articles_list = []

        try:
            if user_id:
                
                article = Articles.objects.filter(author__id=user_id)
                # if article.exists():
                if article:
                    
                    articles_list = self.get_list_of_articles(article)

                    return HttpResponse(
                        json.dumps(articles_list),
                        status=status.HTTP_200_OK,
                    )

            elif slug:
                
                article = Articles.objects.filter(slug=slug)
                # if article.exists():
                if article:
                    
                    articles_list = self.get_list_of_articles(article)

                    return HttpResponse(
                        json.dumps(articles_list),
                        status=status.HTTP_200_OK,
                    )
            else:
                
                print()
                print("*********************************** In List Articles Viewset ************************************ ")
                
                # articles_list = self.get_list_of_articles(self.queryset)
                articles_list = self.get_list_of_articles(Articles.objects.all().order_by('-id'))

            return HttpResponse(
                    json.dumps(articles_list),
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            return Response(
                f'article not found => [ERR]: {e}',
                status=status.HTTP_400_BAD_REQUEST,
            )
        

    @swagger_auto_schema(
        request_body=ArticleSerializer,
        responses = {
            '200' : 'HttpResponse status 201',
            '400': 'article has not been created',
        },
    )

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            
            if "author" not in request.data:
                return Response(json.dumps({
                    # "message": 'category with this title already exists.' if 'unique' in str(e) else str(e),
                    "message": "You must provide an author id !",
                    "data": json.dumps(request.data)
                }), status=status.HTTP_400_BAD_REQUEST)
            
            if not re.match(r'^([\s\d]+)$', str(request.data["author"]) ):
                return Response(json.dumps({
                    # "message": 'category with this title already exists.' if 'unique' in str(e) else str(e),
                    "message": "The author's id must be a digit !",
                    "data": json.dumps(request.data)
                }), status=status.HTTP_400_BAD_REQUEST)
                
            try:
                the_author = User.objects.get(id=int(request.data["author"]))
                
                if not the_author:
                    return Response(json.dumps({
                        "message": "The author's id must be a digit !",
                        "data": json.dumps(request.data)
                    }), status=status.HTTP_400_BAD_REQUEST)
                    
            except Exception as e:
                return Response(json.dumps({
                        # "message": 'category with this title already exists.' if 'unique' in str(e) else str(e),
                        "message": str(e),
                        "data": json.dumps(request.data)
                    }), status=status.HTTP_400_BAD_REQUEST)
                    
            
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            # headers = self.get_success_headers(serializer.data)
            # return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(json.dumps({
                    # "message": 'category with this title already exists.' if 'unique' in str(e) else str(e),
                    "message": str(e),
                    "data": json.dumps(request.data)
                }), status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        request_body=ArticleSerializer,
        responses = {
            '200' : 'HttpResponse status 200',
            '400': 'article has not been updated',
        },
    )

    def update(self, request, slug, *args, **kwargs):

        try:
            
            article = Articles.objects.get(slug=slug)

            if article:
                
                serializer = ArticleSerializer(article, data=request.data)
                # serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)

                serializer.save()

                # print("\n")
                # print("******************** Serializer article Put Method *********************")
                # print("\n")
                # print(serializer.data)

                return Response(serializer.data, status=status.HTTP_200_OK)
            
            else:
                return Response(json.dumps({
                    "message": "article with that slug does not exist",
                    "data": json.dumps(request.data)
                }), status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(json.dumps({
                    # "message": 'category with this title already exists.' if 'unique' in str(e) else str(e),
                    "message": str(e),
                    "data": json.dumps(request.data)
                }), status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        responses = {
            '200' : 'HttpResponse status 200',
            '400': 'article has not been deleted',
        },
    )
    
    def delete(self, request, slug, *args, **kwargs):
        try:
            
            article = Articles.objects.get(slug=slug)

            if article:
                
                if not PublishGroups.objects.filter(articles=article):
                    Comments.objects.filter(article=article).delete()
                    article.delete()
                    
                    return Response(json.dumps({
                        "message": "article has successfully been deleted",
                    }), status=status.HTTP_200_OK)

                return Response(json.dumps({
                    "message": "article belongs to a Published Group, you may not delete it",
                }), status=status.HTTP_401_UNAUTHORIZED)
            
            else:
                return Response(json.dumps({
                    "message": "article with that slug does not exist",
                    "data": json.dumps(request.data)
                }), status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(json.dumps({
                    "message": "article with that slug does not exist" if "Articles matching query does not exist" in str(e) else str(e),
                    "data": json.dumps(request.data)
                }), status=status.HTTP_400_BAD_REQUEST)
            


# ********************************* DONE ************************************************
class CommentsViewSet(ModelViewSet):
    serializer_class = CommentSerializer

    queryset = Comments.objects.all().order_by('-created_at')

    lookup_field = "id"

    def get_serializer(self, data):
        return self.serializer_class(data=data)
    
    def perform_create(self, serializer):
        serializer.save()
    
    def get_list_of_comment(self, comment_objects):
        comment_list = [] 
        
        try:
            for comment in comment_objects:
                
                one_comment = {
                    'id': comment.id,
                    'name': comment.name,
                    'article': { 'id' : comment.article.id, 'title' : comment.article.title, 'slug' : comment.article.slug},
                    'content': comment.content,
                    'created_at': comment.created_at.timestamp(),
                    'modified_at': comment.modified_at.timestamp()
                }

                comment_list.append(one_comment)

            return comment_list
        except Exception as e:
            raise ValidationError(f'[ERR]: category error ==> {e}')
        
        
    article_slug = openapi.Parameter('article_slug', in_=openapi.IN_QUERY, description='article\'s slug to get comments from', type=openapi.TYPE_STRING)

    @swagger_auto_schema(
        manual_parameters=[article_slug])

    # def list(self, request, article_slug, *args, **kwargs):
    def list(self, request, *args, **kwargs):
        article_slug = request.query_params.get('article_slug', None)
        
        comment_list = []
        
        try:
            
            if article_slug:
            
                # print("\n")
                # print("******************************** Got in def list for Comment views set **************************")
                # print("article_slug : ", article_slug)
                # # print("article : ", Articles.objects.get(slug=article_slug))
                # print(Articles.objects.get(slug=article_slug))
                # print("\n")
                
                comments = Comments.objects.filter(article__slug=article_slug)
                
                if not comments:
                    return Response(json.dumps({
                        "message": "No Comments because Article with that slug do not exist",
                        "data": json.dumps(request.data)
                    }), status=status.HTTP_400_BAD_REQUEST)

                comment_list = self.get_list_of_comment(comments)
            
            else:
                
                # comment_list = self.get_list_of_comment(self.queryset)
                comment_list = self.get_list_of_comment(Comments.objects.all().order_by('-created_at'))

            return HttpResponse(
                    json.dumps(comment_list),
                    status=status.HTTP_200_OK,
                )

        except Exception as e:
            return Response(json.dumps({
                    "message": "No comments because Article with that slug does not exist," if "Articles matching query does not exist" in str(e) else str(e),
                    # "message": str(e),
                    "data": json.dumps(request.data)
                }), status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        request_body=CommentSerializer,
        responses = {
            '200' : 'HttpResponse status 201',
            '400': 'comment has not been created',
        },
    )

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(json.dumps({
                    "message": str(e),
                    "data": json.dumps(request.data)
                }), status=status.HTTP_400_BAD_REQUEST)


# ********************************* DONE ************************************************
# class PublishGroupsViewSet(ModelViewSet):
#     serializer_class = PublishGroupsSerializer
#     queryset = PublishGroups.objects.all().order_by('-id')

#     lookup_field = "slug"

#     def get_serializer(self, data):
#         return self.serializer_class(data=data)
    
#     def perform_create(self, serializer):
#         serializer.save()
    
#     def get_list_of_groups(self, groups_objects):
#         groups_list = [] 
        
#         try:
#             for group in groups_objects:
                
#                 articles = []

#                 article_of_group = group.articles.all()

#                 if article_of_group:
#                     articles = [{'id':article.id, 'author': article.author.username, 'title':article.title, 'slug': article.slug} for article in article_of_group]
                
#                 one_group = {
#                     'id': group.id,
#                     'publisher': {'id':group.publisher.id, 'username':group.publisher.username, 'user_type': group.publisher.get_user_type_display() },
#                     'title': group.title,
#                     'slug': group.slug, 
#                     'description': group.description,
#                     'articles': articles,
#                     'photo': "" if not group.photo else group.photo.url,
#                     'created_at': group.created_at.timestamp(),
#                     'modified_at': group.modified_at.timestamp()
#                 }

#                 groups_list.append(one_group)

#             return groups_list
#         except Exception as e:
#             raise ValidationError(f'[ERR]: Publish Group error ==> {e}')

        
#     slug = openapi.Parameter('slug', in_=openapi.IN_QUERY, description='Publish Group\'s slug', type=openapi.TYPE_STRING)
    
#     user_id = openapi.Parameter('user_id', in_=openapi.IN_QUERY, description='Publisher\'s id', type=openapi.TYPE_INTEGER)
    

#     @swagger_auto_schema(
#         manual_parameters=[slug, user_id])

#     def list(self, request, *args, **kwargs):
#         slug = request.query_params.get('slug', None)
#         user_id = request.query_params.get('user_id', None)
        
#         groups_list = []

#         try:
#             if user_id:
                
#                 group = PublishGroups.objects.filter(publisher__id=user_id)
#                 # if article.exists():
#                 if group:
                    
#                     groups_list = self.get_list_of_articles(group)

#                     return HttpResponse(
#                         json.dumps(groups_list),
#                         status=status.HTTP_200_OK,
#                     )

#             elif slug:
                
#                 group = PublishGroups.objects.filter(slug=slug)
#                 # if article.exists():
#                 if group:
                    
#                     groups_list = self.get_list_of_articles(group)
#             else:
#                 groups_list = self.get_list_of_groups(PublishGroups.objects.all().order_by('-id'))

#             return HttpResponse(
#                     json.dumps(groups_list),
#                     status=status.HTTP_200_OK,
#                 )
#         except Exception as e:
#             return Response(
#                 f'article not found => [ERR]: {e}',
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
        

#     @swagger_auto_schema(
#         request_body=ArticleSerializer,
#         responses = {
#             '200' : 'HttpResponse status 201',
#             '400': 'article has not been created',
#         },
#     )

#     def create(self, request, *args, **kwargs):
#         try:
#             serializer = self.get_serializer(data=request.data)
#             serializer.is_valid(raise_exception=True)
#             self.perform_create(serializer)
#             # headers = self.get_success_headers(serializer.data)
#             # return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#         except Exception as e:
#             return Response(json.dumps({
#                     # "message": 'category with this title already exists.' if 'unique' in str(e) else str(e),
#                     "message": str(e),
#                     "data": json.dumps(request.data)
#                 }), status=status.HTTP_400_BAD_REQUEST)


#     @swagger_auto_schema(
#         request_body=ArticleSerializer,
#         responses = {
#             '200' : 'HttpResponse status 200',
#             '400': 'article has not been updated',
#         },
#     )

#     def update(self, request, slug, *args, **kwargs):

#         try:
            
#             article = Articles.objects.get(slug=slug)

#             if article:
                
#                 serializer = ArticleSerializer(article, data=request.data)
#                 # serializer = self.get_serializer(data=request.data)
#                 serializer.is_valid(raise_exception=True)

#                 serializer.save()

#                 # print("\n")
#                 # print("******************** Serializer article Put Method *********************")
#                 # print("\n")
#                 # print(serializer.data)

#                 return Response(serializer.data, status=status.HTTP_200_OK)
            
#             else:
#                 return Response(json.dumps({
#                     "message": "article with that slug does not exist",
#                     "data": json.dumps(request.data)
#                 }), status=status.HTTP_400_BAD_REQUEST)

#         except Exception as e:
#             return Response(json.dumps({
#                     # "message": 'category with this title already exists.' if 'unique' in str(e) else str(e),
#                     "message": str(e),
#                     "data": json.dumps(request.data)
#                 }), status=status.HTTP_400_BAD_REQUEST)


#     @swagger_auto_schema(
#         responses = {
#             '200' : 'HttpResponse status 200',
#             '400': 'article has not been deleted',
#         },
#     )
    
#     def delete(self, request, slug, *args, **kwargs):
#         try:
            
#             article = Articles.objects.get(slug=slug)

#             if article:
                
#                 if not PublishGroups.objects.filter(articles=article):
#                     Comments.objects.filter(article=article).delete()
#                     article.delete()
                    
#                     return Response(json.dumps({
#                         "message": "article has successfully been deleted",
#                     }), status=status.HTTP_200_OK)

#                 return Response(json.dumps({
#                     "message": "article belongs to a Published Group, you may not delete it",
#                 }), status=status.HTTP_401_UNAUTHORIZED)
            
#             else:
#                 return Response(json.dumps({
#                     "message": "article with that slug does not exist",
#                     "data": json.dumps(request.data)
#                 }), status=status.HTTP_400_BAD_REQUEST)

#         except Exception as e:
#             return Response(json.dumps({
#                     "message": "article with that slug does not exist" if "Articles matching query does not exist" in str(e) else str(e),
#                     "data": json.dumps(request.data)
#                 }), status=status.HTTP_400_BAD_REQUEST)
        
        
        