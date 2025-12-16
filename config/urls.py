from django.conf.urls.static import static
from django.urls import path, include, re_path

from config import settings
from rest_framework import permissions

# ### Swagger
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from config.shared.constants.envs_constants import env

schema_view = get_schema_view(
    openapi.Info(
        title="ERP API",
        default_version='v1',
        description="API description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@myapi.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    url=env.str('API_BASE_URL')
)

urlpatterns = [
    # ### Swagger
    re_path(r'^api/v1/swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/v1/swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),

    path("api/v1/role/", include("log.urls.role_urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
