from django.db.models import JSONField
from django_filters import rest_framework as filters

from config.shared.filters.filters import BaseFilter
from users.models.custom_group_model import CustomGroup


class CustomGroupFilter(BaseFilter):
    class Meta:
        filter_overrides = {
            JSONField: {
                'filter_class': filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
        }
        model = CustomGroup
        fields = '__all__'
