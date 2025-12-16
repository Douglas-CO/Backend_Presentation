from django.urls import path


from users.views.auth_view import (
    AuthView, logout, get_permissions, get_permissions_group,
)
from users.views.general_view import (
    get_system_modules, generate_temporary_upload_link
)
from users.views.custom_group_views import (
    CustomGroupView, CustomGroupDetailView, CustomGroupDetailViewByUuid
)
from users.views.totp_views import (
    TOTPSetupInitView, TOTPSetupConfirmView, TOTPDisableView,
    totp_status, TOTPBackupRegenerateView
)


urlpatterns = [

    path("login/", AuthView.as_view(), name="login"),
    path("logout/", logout, name="logout"),
    path("system-modules-sidenav/", get_system_modules, name="system-modules"),


    path("totp/setup/init/", TOTPSetupInitView.as_view(), name="totp-setup-init"),
    path("totp/setup/confirm/", TOTPSetupConfirmView.as_view(),
         name="totp-setup-confirm"),
    path("totp/disable/", TOTPDisableView.as_view(), name="totp-disable"),
    path("totp/status/", totp_status, name="totp-status"),
    path("totp/backup/regenerate/", TOTPBackupRegenerateView.as_view(),
         name="totp-backup-regenerate"),
    # ------------

    # permissions
    path("permissions/", get_permissions, name="permissions"),
    path("permissions/group/<int:pk>/",
         get_permissions_group, name="permissions-group"),

    # groups
    path('group/', CustomGroupView.as_view(), name='custom-groups'),
    path('group/<int:pk>/', CustomGroupDetailView.as_view(),
         name='custom-groups-detail'),
    path('group/uuid/<str:uuid>/', CustomGroupDetailViewByUuid.as_view(),
         name='custom-group-detail-uuid'),

    # MinIO
    path('generate-temporary-upload-link/', generate_temporary_upload_link,
         name='generate-temporary-upload-link'),

]
