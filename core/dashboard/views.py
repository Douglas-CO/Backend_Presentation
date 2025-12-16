import json
from drf_yasg.utils import swagger_auto_schema

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views.generic import TemplateView

from core.billing.models import Customer, Contract, Invoice, CONTRACT_STATUS
from core.multicpy.models import Company


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
        if not self.request.tenant.is_public():
            if self.request.user.is_customer():
                context['invoices'] = Invoice.objects.filter(
                    customer__user=self.request.user).order_by('-id')[0:10]
            else:
                context['customers'] = Customer.objects.filter()
                context['contracts'] = Contract.objects.filter().exclude(
                    status=CONTRACT_STATUS[-1][0])
                context['invoices'] = Invoice.objects.filter().order_by(
                    '-id')[0:10]
        else:
            context['companies'] = Company.objects.all()
        return context
