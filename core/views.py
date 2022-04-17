from rest_framework import exceptions
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import get_authorization_header

from .authentication import JWTAuthentication, create_access_token, create_refresh_token, decode_refresh_token
from .models import User

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
    def post(self,request):
        refresh_token=request.COOKIES.get('refresh_token')
        id=decode_refresh_token(refresh_token)
        access_token=create_access_token(id)
        return Response({
            'token':access_token
        })