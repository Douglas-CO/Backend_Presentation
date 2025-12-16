from django.urls import path

from log.views.role_views import (
    RoleView,
    RoleDetailView,
    RoleDetailViewByUuid,
)


urlpatterns = [
    path('', RoleView.as_view(), name='role'),
    path('<int:pk>/', RoleDetailView.as_view(), name='role-detail'),
    path('<str:uuid>/', RoleDetailViewByUuid.as_view(), name='role-detail-uuid'),
]
