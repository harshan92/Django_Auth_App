from dataclasses import fields
from pyexpat import model
from rest_framework.serializers import ModelSerializer
from .models import User

class UserSerializer(ModelSerializer):
    class Meta:
        model=User
        fields=['id','first_name','last_name','email','password']