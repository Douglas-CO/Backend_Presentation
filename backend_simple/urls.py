from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="API Simple",
        default_version="v1",
        description="Documentación generada con Swagger",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


def root_redirect(request):
    return redirect('/swagger/')


urlpatterns = [
    path('', root_redirect),
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0)),

    # Tus endpoints de la app
    path("auth/", include("usuarios.urls")),
]
