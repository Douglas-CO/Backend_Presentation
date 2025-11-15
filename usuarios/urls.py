from django.urls import path
from .views import RegistroView, LoginView

urlpatterns = [
    path("register/", RegistroView.as_view()),
    path("login/", LoginView.as_view()),
]
