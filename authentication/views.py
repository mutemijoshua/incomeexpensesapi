from django.shortcuts import render

from rest_framework import generics,status,views
from .serializers import (RegisterSerializer, EmailVerificationSErializer,LoginSerializer,ResetPasswordEmailRequestSerializer
         ,TokenCheckSerializer, SetNewPasswordserializer,LogoutSerializer)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
from .models import User
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .renderers import UserRenderer
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str,force_str,force_bytes,DjangoUnicodeDecodeError,smart_bytes
from django.utils.http import urlsafe_base64_decode , urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import Util
from rest_framework import permissions
# Create your views here.

class RegisterView(generics.GenericAPIView):
    serializer_class=RegisterSerializer

   # renderer_classes =(UserRenderer)
    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user = User.objects.get(email=user_data['email'])
        token = RefreshToken.for_user(user).access_token

        current_site = get_current_site(request).domain
        relativeLink = reverse('email-verify')
        absurl = 'http://'+current_site+relativeLink+"?token="+str(token) 
        email_body= 'Hi'+user.username+'use link below to verify your email \n' + absurl
        data = {'email_body': email_body,'to_email':user.email,'email_subject':'Verify your email'}
        Util.send_email(data)
        return Response(user_data,status=status.HTTP_201_CREATED)
    
class VerifyEmail(views.APIView):
    serializer_class = EmailVerificationSErializer
    token_param_config = openapi.Parameter('token',in_=openapi.IN_QUERY,description="Description",type=openapi.TYPE_STRING)
    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self,request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY,algorithms='HS256')
            user = User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return Response({'email': 'Successfully activated'},status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error':'Activation link expired'},status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifire:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(generics.GenericAPIView):
    serializer_class=LoginSerializer
    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data,status.HTTP_200_OK)
        
class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer
    def post(self, request):
        data = {'request':request,'data': request.data}
        serializer = self.serializer_class(data=request.data)
        email = request.data['email']
        if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
                token = PasswordResetTokenGenerator().make_token(user)
                redirect_url=request.data.get('redirect_url'+"")
                current_site = get_current_site(request=request).domain
                relativeLink = reverse('password-reset-confirm',kwargs={'uidb64':uidb64,'token':token})
                absurl = 'http://'+current_site+relativeLink
                email_body= 'Hello '+user.username+' use link to reset your password \n' + absurl+"?redirect_url="+redirect_url,
                data = {'email_body': email_body,'to_email':user.email,'email_subject':'Reset your password'}
                Util.send_email(data) 
    


        return Response({'Success ': ' We have sent you a link to reset your password'},status=status.HTTP_200_OK)

class PasswordTokenCheckAPI(generics.GenericAPIView):
    serializer_class = TokenCheckSerializer 
    def get(self,request,uidb64,token):
    
        try:
            id=smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
 
            if not PasswordResetTokenGenerator().check_token(user,token):
              return Response({'error':'Token is not valid, please request a new one'})
            return Response({'Success': True,'message': ' credentials Valid','uidb64' :uidb64, 'token': token},status=status.HTTP_200_OK) 
        
        
        except DjangoUnicodeDecodeError as identifier:
            return Response({'error': 'Token is not valid, please request a new one'})

class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class=SetNewPasswordserializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception = True)
        return Response({'success':True,'message': 'Password reset success'}, status=status.HTTP_200_OK)
    
class LogoutAPIView(generics.GenericAPIView):
    serializer_class=LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self,request):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exeption=True)

        return Response(status.HTTP_204_NO_CONTENT)