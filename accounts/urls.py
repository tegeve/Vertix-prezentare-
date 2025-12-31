from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import register, EmailLoginView

urlpatterns = [
    path("inregistrare/", register, name="register"),
    path("login/", EmailLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
