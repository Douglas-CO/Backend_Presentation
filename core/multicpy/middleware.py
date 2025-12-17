# core/multicpy/middleware.py
# from django.http import HttpResponseForbidden


class CustomMiddleware:
    """
    Middleware simplificado sin tenants.
    Aquí puedes poner cualquier lógica de validación global de request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Lógica antes de la vista
        # Por ejemplo, si quieres bloquear requests basados en headers, IP, etc.
        # if some_condition:
        #     return HttpResponseForbidden("No autorizado")

        response = self.get_response(request)
        # Lógica después de la vista (opcional)
        return response
