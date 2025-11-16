from django.urls import path
from .views import RegistroView, LoginView, GrupoDetailView, GrupoListCreateView, UsuarioListView, UsuarioDetailView

urlpatterns = [
    path("register/", RegistroView.as_view()),
    path("login/", LoginView.as_view()),
    path("grupo/", GrupoListCreateView.as_view()),
    path("grupo/<int:pk>/", GrupoDetailView.as_view()),
    path("users/", UsuarioListView.as_view()),
    path("users/<int:pk>/", UsuarioDetailView.as_view())
]
