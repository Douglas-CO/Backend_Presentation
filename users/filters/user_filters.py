from django.db.models import JSONField
from django_filters import rest_framework as filters

from config.shared.filters.filters import BaseFilter
from users.models.usuario_model import Usuario

import django_filters


class UserFilter(BaseFilter):

    is_blocked = django_filters.BooleanFilter(method='filter_is_blocked')

    class Meta:
        filter_overrides = {
            JSONField: {
                'filter_class': filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
        }
        model = Usuario
        fields = "__all__"

    def filter_is_blocked(self, queryset, name, value):
        return queryset.filter(intentos_fallidos__gte=3) if value else queryset
