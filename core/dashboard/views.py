import json
from drf_yasg.utils import swagger_auto_schema

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views.generic import TemplateView


class DashboardView(LoginRequiredMixin, TemplateView):
    def get_template_names(self):
        if self.request.tenant.is_public():
            return 'panel_admin.html'
        elif self.request.user.is_customer():
            return 'panel_customer.html'
        return 'panel_company.html'

    @swagger_auto_schema(auto_schema=None)
    def post(self, request, *args, **kwargs):
        data = {}
        return HttpResponse(json.dumps(data), content_type='application/json')

    @swagger_auto_schema(auto_schema=None)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Panel de Administración'
        print(context)
