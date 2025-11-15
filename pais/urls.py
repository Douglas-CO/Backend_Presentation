from rest_framework.routers import DefaultRouter
from .views import PaisListCreateView, PaisDetailView
from django.urls import path

urlpatterns = [
    path("", PaisListCreateView.as_view()),
    path("<int:pk>/", PaisDetailView.as_view()),
]
