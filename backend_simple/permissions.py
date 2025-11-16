from rest_framework.permissions import BasePermission

class RequirePermission(BasePermission):
    permission_map = {}

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        grupo = getattr(request.user, "grupo", None)
        if not grupo:
            return False

        required_perm = self.permission_map.get(request.method)
        if not required_perm:
            return True

        return required_perm in grupo.permissions
    

class UsuarioPermission(RequirePermission):
    permission_map = {
        "GET": "administration.view_usuario",
        "PATCH": "administration.change_usuario",
        # POST ya lo controla /auth/register/
    }