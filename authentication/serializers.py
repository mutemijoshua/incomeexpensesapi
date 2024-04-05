#create a serializer class for the views
from rest_framework import serializers
from .models import User
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str,force_str,force_bytes,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode , urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken,TokenError
from .utils import Util


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68,min_length=6,write_only=True)

    class Meta:
        model = User 
        fields = ['email','username','password']
    
    def validate(self, attrs):
        email = attrs.get('email', '')
        username = attrs.get('username', '')
        
        if not username.isalnum():
             raise serializers.ValidationError('The username should only contain alphanumeric characters')
        return attrs
    
    
    def create(self,validated_data):
        return User.objects.create_user(**validated_data)
    
class EmailVerificationSErializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=255)
    class Meta:
        model = User
        fields = ['token']

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length = 255,min_length = 3)
    password = serializers.CharField(max_length=68,min_length=6,write_only=True)
    username = serializers.CharField(max_length=255,min_length=3,read_only=True)
    tokens=serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['email','password','username','tokens']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        filtered_user_by_email = User.objects.filter(email=email)
        user = auth.authenticate(email=email, password=password)

        if filtered_user_by_email.exists() and filtered_user_by_email[0].auth_provider != 'email':
            raise AuthenticationFailed(
                detail='Please continue your login using ' + filtered_user_by_email[0].auth_provider)


        if not user:
            raise AuthenticationFailed('Invalid credentials try again')
        if not user.is_active:
             raise AuthenticationFailed('Account disabled contact admin') 
        if not user.is_verified:
             raise AuthenticationFailed('Invalid credentials,try again')
        attrs= {
                'email':user.email,
                'username':user.username,
                'tokens':user.tokens }
        
        return super().validate(attrs)
    
class ResetPasswordEmailRequestSerializer(serializers.Serializer):

    email = serializers.EmailField(min_length=2)

    redirect_url = serializers.CharField(max_length=500,required=False)

    class Meta:
        fields = ['email']
class TokenCheckSerializer(serializers.Serializer):

    token = serializers.CharField(max_length = 255)
    uidb64 = serializers.CharField(max_length = 255)

    class Meta:
        fields = [ 'token','uidb64']

class SetNewPasswordserializer(serializers.Serializer):
    password = serializers.CharField(min_length = 6,max_length = 68,write_only=True)
    token = serializers.CharField(min_length = 1,write_only=True)
    uidb64 = serializers.CharField(min_length = 1,write_only=True)

    class Meta:
        fields = ['password','token','uidb64']

    def validate(self, attrs):
        try:
            password=attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid',401)
            user.set_password(password)
            user.save()
            return (user)
        except  Exception as e:
            raise AuthenticationFailed('The reset link is invalid')  
        return super().validate(attrs)


class LogoutSerializer(serializers.Serializer):
        refresh = serializers.CharField()

        default_error_messages = {
            'bad_token':"Token is expired or invalid"
        }

        
        def validate(self,attrs):
            self.token = attrs['refresh']
            return attrs
        
        def save(self, **kwargs):
            try:
                RefreshToken(self.token).blacklist()
            except TokenError :
                self.fail('bad_token')
        