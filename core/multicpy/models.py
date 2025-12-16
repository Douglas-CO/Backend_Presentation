from django.db import models
from django.forms import model_to_dict
from django_tenants.models import TenantMixin, DomainMixin


class Scheme(TenantMixin):
    name = models.CharField(max_length=100)
    created_on = models.DateField(auto_now_add=True)
    auto_create_schema = True

    def get_full_domain(self):
        domain_ = self.domains.first()
        if domain_:
            return domain_.domain
        return None

    def is_public(self):
        return self.name.lower() == 'public'

    def as_dict(self):
        item = model_to_dict(self, exclude=['created_on'])
        return item

class Domain(DomainMixin):
    pass
