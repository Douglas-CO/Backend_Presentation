from django.urls import path

from users.views.user_view import (
    user_create_view, get_all, UserDetailUUIDView, UserDetailView, UnblockUserView,
    ChangePasswordView, DeactivateUserView
)

urlpatterns = [
    path("", user_create_view, name="user_create"),
    path("all/", get_all, name="get_all"),

    path('unblock/<int:pk>/', UnblockUserView.as_view(), name='unblock-user'),
    path('change-password/<int:id>/',
         ChangePasswordView.as_view(), name='change-password'),
    path('deactivate/<int:id>/', DeactivateUserView.as_view(),
         name='deactivate-user'),

    path('uuid/<str:uuid>/', UserDetailUUIDView.as_view(), name='user-detail-uuid'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
]
