from django.contrib.auth import authenticate, login, get_user_model
from django.contrib import auth
from rest_framework import serializers 
# from rest_framework.serializers import FileField
from rest_framework.exceptions import AuthenticationFailed

from account.models import *
from blog.models import *

from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator



# ******************************************************* 
# *****                                             *****
# *****            Account Web Service              *****
# *****                                             *****
# *******************************************************



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "username", "password"]


    def create(self, validated_data):
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        username = validated_data['username']
        password = validated_data['password']
        email = validated_data['email']

        try:
            user_exist = User.objects.get(email=validated_data['email'])
            if user_exist:
                raise AuthenticationFailed('User with this email already exists.') 
        except User.DoesNotExist:
            pass

        return User.objects.create_user(first_name=first_name, last_name=last_name, username=username, password=password, email=email, user_type='1')


class LoginSerializer(serializers.ModelSerializer):
    
    username = serializers.CharField(max_length=255, min_length=2)
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    client_id = serializers.CharField(max_length=68, min_length=6, write_only=True)
    client_secret = serializers.CharField(max_length=128, min_length=6, write_only=True)
    email = serializers.CharField(max_length=68, read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "password", "email", "client_id", "client_secret"]

    def validate(self, attrs):
        username = attrs.get("username", "")
        password = attrs.get("password", "")
        client_id = attrs.get("client_id", "")
        client_secret = attrs.get("client_secret", "")

        try:

            filtered_user_by_username = User.objects.get(username=username)

            user = authenticate(username=username, password=password)

            if not user:
                raise AuthenticationFailed("Invalid credentials, try again")  # A traduire

            if not user.is_active:
                raise AuthenticationFailed("Account disabled, contact admin")  # A traduire

            if not filtered_user_by_username.is_superuser:
                
                if not filtered_user_by_username.is_active:
                    raise AuthenticationFailed("Email is not verified")  # A traduire

            return {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "user_type": user.get_user_type_display(),  # get_enquete_type_display()
                "password": password,
                "client_id": client_id,
                "client_secret": client_secret,
            }
        except User.DoesNotExist:
            raise AuthenticationFailed(
                "Account has no email provided"
            )  # A traduire



"""
    BUG : the url must come from the api consumer 
"""
# To Check for the redirect url Bug  
class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2, required=True)
    # redirect_url = serializers.CharField(max_length=500, required=True)

    class Meta:
        fields = ['email']
        
        
        
class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401) 

            user.set_password(password)
            user.save()
            return (user)
        except Exception:
            raise AuthenticationFailed('The reset link is invalid', 401)

        return super().validate(attrs)



# ******************************************************* 
# *****                                             *****
# *****            Blog Web Service              *****
# *****                                             *****
# *******************************************************

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "title", "slug", "description", "created_at", "modified_at"]
            
            
class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Articles
        fields = ["id", "author", "category", "title", "slug", "content", "photo", "read_by", "liked_by", "created_at", "modified_at"]            
            
            
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = ["id", "name", "article", "content", "created_at", "modified_at"]


class PublishGroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublishGroups
        fields = ["id", "publisher", "title", "slug", "description", "articles", "description", "photo", "created_at", "modified_at"]


class DemandsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Demands
        fields = ["id", "author", "publish_group", "article", "content", "created_at", "modified_at"]



class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", "email", "user_type", "created_at", "modified_at"]
        
        
        