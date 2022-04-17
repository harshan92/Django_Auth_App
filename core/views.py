from cgitb import reset
import datetime
import email
from email import message
import random
import string
from rest_framework import exceptions
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import get_authorization_header
from django.core.mail import send_mail

from .authentication import JWTAuthentication, create_access_token, create_refresh_token, decode_refresh_token
from .models import Reset, User, UserToken

from .serializers import UserSerializer

class RegisterAPIView(APIView):
    def post(self, request):
        data=request.data
        
        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('passwords do not match')
        
        serializer=UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class LoginAPIView(APIView):
    def post(self, request):
        email=request.data['email']
        password=request.data['password']

        user=User.objects.filter(email=email).first()

        if user is None:
            raise exceptions.APIException('Invalid credentials')

        if not user.check_password(password):
            raise exceptions.APIException('Invalid credentials')

        access_token=create_access_token(user.id)
        refresh_token=create_refresh_token(user.id)

        UserToken.objects.create(
            user_id=user.id,
            token=refresh_token,
            expired_at=datetime.datetime.utcnow()+datetime.timedelta(days=7)
        )
        serializer=UserSerializer(user)

        response=Response()

        response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
        
        response.data={
            "token":access_token
        }

        return response

class UserAPIView(APIView):
    authentication_classes=[JWTAuthentication]
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class RefreshAPIView(APIView):
    authentication_classes=[JWTAuthentication]
    def post(self,request):
        refresh_token=request.COOKIES.get('refresh_token')
        id=decode_refresh_token(refresh_token)
        print(id)
        print(refresh_token)
        if not UserToken.objects.filter(user_id=id, token=refresh_token,expired_at__gt=datetime.datetime.now(tz=datetime.timezone.utc)).exists():
            raise exceptions.APIException('unauthenticated')
        
        access_token=create_access_token(id)
        return Response({
            'token':access_token
        })

class LogoutAPIView(APIView):
    authentication_classes=[JWTAuthentication]
    def post(self, request):
        UserToken.objects.filter(user_id=request.user.id).delete()
        response=Response()
        response.delete_cookie(key="refresh_token")
        response.data={
            "message":"success"
        }

        return response

class ForgotAPIView(APIView):
    def post(self, request):
        token=''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
        email=request.data['email']
        Reset.objects.create(
            email=email,
            token=token
        )
        
        url='http://localhost:3000/reset/'+token

        send_mail(
            subject="Reset your password",
            message='Click <a href="%s">here</a> to reset your password' % url,
            from_email='from@example.com',
            recipient_list=[email]
        )

        return Response({
            'message':'success'
        })

class ResetAPIView(APIView):
    def post(self, request):
        data=request.data
        
        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('passwords do not match')
        
        reset_password=Reset.objects.filter(token=data["token"]).first()

        if not reset_password:
            raise exceptions.APIException('invalid link')
        
        user=User.objects.filter(email=reset_password.email).first()

        if not user:
            raise exceptions.APIException('user not found')

        user.set_password(data["password"])
        user.save()

        return Response({
            "message":"success"
        })
