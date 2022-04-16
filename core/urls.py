from .views import RegisterAPIView, LoginAPIView, UserAPIView
from django.urls import path, include

urlpatterns = [
    path('register', RegisterAPIView.as_view()),
    path('login', LoginAPIView.as_view()),
    path('user', UserAPIView.as_view()),
]