from django.urls import path
from .views import ProvinciaListCreateView, ProvinciaDetailView

urlpatterns = [
    path("", ProvinciaListCreateView.as_view()),
    path("<int:pk>/", ProvinciaDetailView.as_view()),
]
