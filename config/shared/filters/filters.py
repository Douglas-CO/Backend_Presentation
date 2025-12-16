import django_filters
from django.db.models import (
    ForeignKey,
    OneToOneField,
    CharField,
    DateField,
    DateTimeField,
    JSONField,
    UUIDField,
    IntegerField,
    FloatField,
    BooleanField,
    DecimalField,
    GenericIPAddressField,
)
from django.core.exceptions import ValidationError
from functools import lru_cache


class SafeFKFilter(django_filters.CharFilter):
    def filter(self, qs, value):
        if value in (None, ''):
            return qs
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            return qs.none()
        return super().filter(qs, int_value)


class SafeNumberFilter(django_filters.NumberFilter):
    def filter(self, qs, value):
        try:
            if value in (None, ''):
                return qs
            return super().filter(qs, value)
        except (ValueError, TypeError, ValidationError):
            return qs.none()


class JSONArrayContainsFilter(django_filters.CharFilter):
    def filter(self, qs, value):
        if value in (None, ''):
            return qs

        try:
            value = int(value)
        except (ValueError, TypeError):
            pass

        return qs.filter(**{f'{self.field_name}__contains': [value]})


class BaseFilter(django_filters.FilterSet):
    # Configuración de optimización
    ENABLE_DEEP_FILTERING = True
    MAX_FK_DEPTH = 3
    ENABLE_REVERSE_RELATIONS = True
    LAZY_LOADING = True

    def filter_exclude_field(self, queryset, name, value):
        return queryset.exclude(**{name + '__in': value})

    @lru_cache(maxsize=500)
    def _get_model_fields_info(self, model):
        """Cache información de campos del modelo."""
        fields_info = {}
        for field in model._meta.fields:
            if hasattr(field, 'name'):
                fields_info[field.name] = {
                    'field': field,
                    'type': type(field).__name__,
                    'is_fk': isinstance(field, (ForeignKey, OneToOneField)),
                    'is_pk': field.primary_key,
                    'choices': getattr(field, 'choices', None),
                    'related_model': getattr(field, 'related_model', None) if isinstance(field, (ForeignKey, OneToOneField)) else None
                }
        return fields_info

    @lru_cache(maxsize=500)
    def _get_reverse_relations_info(self, model):
        """Cache información de relaciones inversas con mejor detección."""
        relations_info = {}

        # Obtener relaciones inversas (reverse relations)
        for relation in model._meta.related_objects:
            accessor_name = relation.get_accessor_name()

            # Determinar el tipo de relación
            if hasattr(relation, 'one_to_one') and relation.one_to_one:
                relations_info[accessor_name] = {
                    'type': 'one_to_one',
                    'related_model': relation.related_model,
                    'relation': relation,
                    'field_name': relation.field.name,
                    'is_reverse': True
                }
            elif hasattr(relation, 'many_to_one') and relation.many_to_one:
                relations_info[accessor_name] = {
                    'type': 'many_to_one',
                    'related_model': relation.related_model,
                    'relation': relation,
                    'field_name': relation.field.name,
                    'is_reverse': True
                }
            elif hasattr(relation, 'many_to_many') and relation.many_to_many:
                relations_info[accessor_name] = {
                    'type': 'many_to_many',
                    'related_model': relation.related_model,
                    'relation': relation,
                    'field_name': relation.field.name,
                    'is_reverse': True
                }

        return relations_info

    def _get_requested_filters(self):
        """Obtiene solo los filtros que están en la request."""
        if not hasattr(self, 'data') or not self.data:
            return set()

        # Obtener todas las keys de los parámetros de la request
        requested_keys = set(self.data.keys())

        # Agregar variaciones comunes que podrían necesitarse
        extended_keys = set(requested_keys)
        for key in requested_keys:
            if key.endswith('_in'):
                base_key = key[:-3]
                extended_keys.add(base_key)
                extended_keys.add(f'{base_key}_exact')
            elif key.endswith('_exact'):
                base_key = key[:-6]
                extended_keys.add(base_key)

        return extended_keys

    def add_fk_filters(self, field, prefix, depth, max_depth, requested_filters=None):
        """
        Agrega recursivamente filtros para campos del modelo relacionado (FK).
        Mejorado para manejar mejor las relaciones.
        """
        if depth > max_depth:
            return

        related_model = field.related_model

        # Procesar campos directos del modelo relacionado
        for related_field in related_model._meta.fields:
            related_field_name = related_field.name
            full_filter_name = f'{prefix}{related_field_name}'

            # Si lazy loading está activado, solo construir filtros solicitados
            if self.LAZY_LOADING and requested_filters is not None:
                should_build = any(
                    req_filter.startswith(full_filter_name)
                    for req_filter in requested_filters
                )
                if not should_build:
                    continue

            self._add_field_filters(related_field, full_filter_name)

            # Recursividad para ForeignKey/OneToOneField
            if depth < max_depth and isinstance(related_field, (ForeignKey, OneToOneField)):
                self.add_fk_filters(
                    related_field,
                    full_filter_name + '__',
                    depth + 1,
                    max_depth,
                    requested_filters
                )

    def add_reverse_relation_filters(self, relation_info, prefix, depth, max_depth, requested_filters=None):
        """
        Agrega filtros para relaciones inversas mejorado.
        """
        if depth > max_depth:
            return

        related_model = relation_info['related_model']

        # Procesar campos del modelo relacionado
        for related_field in related_model._meta.fields:
            related_field_name = related_field.name
            full_filter_name = f'{prefix}{related_field_name}'

            # Si lazy loading está activado, solo construir filtros solicitados
            if self.LAZY_LOADING and requested_filters is not None:
                should_build = any(
                    req_filter.startswith(full_filter_name)
                    for req_filter in requested_filters
                )
                if not should_build:
                    continue

            self._add_field_filters(related_field, full_filter_name)

            # Recursividad para ForeignKey/OneToOneField
            if depth < max_depth and isinstance(related_field, (ForeignKey, OneToOneField)):
                self.add_fk_filters(
                    related_field,
                    full_filter_name + '__',
                    depth + 1,
                    max_depth,
                    requested_filters
                )

    def _add_field_filters(self, field, field_name):
        """
        Método auxiliar para agregar filtros según el tipo de campo.
        Centraliza la lógica de creación de filtros.
        """
        #    __in
        self.filters[f'{field_name}_in'] = django_filters.BaseInFilter(
            field_name=field_name,
            lookup_expr='in'
        )

        if field.primary_key:
            if isinstance(field, UUIDField):
                self.filters[field_name] = django_filters.CharFilter(
                    field_name=field_name, lookup_expr='iexact'
                )
            else:
                self.filters[field_name] = SafeNumberFilter(
                    field_name=field_name, lookup_expr='exact'
                )
            self.filters[f'{field_name}_in'] = django_filters.BaseInFilter(
                field_name=field_name, lookup_expr='in'
            )
            return  # Early return para evitar duplicados

        if isinstance(field, GenericIPAddressField):
            self.filters[field_name] = django_filters.CharFilter(
                field_name=field_name,
                lookup_expr='exact'
            )
            self.filters[f'{field_name}__contains'] = django_filters.CharFilter(
                field_name=field_name,
                lookup_expr='icontains'
            )
            self.filters[f'{field_name}__in'] = django_filters.BaseInFilter(
                field_name=field_name,
                lookup_expr='in'
            )
            return

        if isinstance(field, CharField):
            if field.choices:
                self.filters[field_name] = django_filters.ChoiceFilter(
                    field_name=field_name,
                    choices=field.choices,
                    lookup_expr='exact'
                )
                self.filters[f'{field_name}__contains'] = django_filters.CharFilter(
                    field_name=field_name,
                    lookup_expr='icontains'
                )
            else:
                self.filters[field_name] = django_filters.CharFilter(
                    field_name=field_name,
                    lookup_expr='icontains'
                )
                self.filters[field_name + '_exact'] = django_filters.CharFilter(
                    field_name=field_name,
                    lookup_expr='exact'
                )
        elif isinstance(field, IntegerField):
            self.filters[field_name + '_exact'] = SafeNumberFilter(
                field_name=field_name,
                lookup_expr='exact'
            )
        elif isinstance(field, BooleanField):
            self.filters[field_name] = django_filters.BooleanFilter(
                field_name=field_name
            )
        elif isinstance(field, (DateField, DateTimeField)):
            self.filters[field_name + '_range'] = django_filters.DateFromToRangeFilter(
                field_name=field_name
            )
            self.filters[field_name + '_exact'] = django_filters.DateFilter(
                field_name=field_name,
                lookup_expr='exact'
            )
        elif isinstance(field, JSONField):
            self.filters[field_name] = django_filters.CharFilter(
                field_name=field_name,
                lookup_expr='icontains'
            )
            self.filters[f'{field_name}_exact_array'] = JSONArrayContainsFilter(
                field_name=field_name
            )
        elif isinstance(field, (FloatField, DecimalField)):
            self.filters[f'{field_name}_range'] = django_filters.RangeFilter(
                field_name=field_name
            )
            self.filters[f'{field_name}_exact'] = SafeNumberFilter(
                field_name=field_name,
                lookup_expr='exact'
            )
        elif isinstance(field, UUIDField):
            self.filters[field_name] = django_filters.CharFilter(
                field_name=field_name,
                lookup_expr="iexact"
            )

    def __init__(self, *args, **kwargs):
        # Configuración por instancia
        self.ENABLE_DEEP_FILTERING = kwargs.pop(
            'enable_deep_filtering', self.ENABLE_DEEP_FILTERING)
        self.MAX_FK_DEPTH = kwargs.pop('max_fk_depth', self.MAX_FK_DEPTH)
        self.ENABLE_REVERSE_RELATIONS = kwargs.pop(
            'enable_reverse_relations', self.ENABLE_REVERSE_RELATIONS)
        self.LAZY_LOADING = kwargs.pop('lazy_loading', self.LAZY_LOADING)

        super().__init__(*args, **kwargs)

        # Obtener filtros solicitados si lazy loading está activado
        requested_filters = self._get_requested_filters() if self.LAZY_LOADING else None

        model_fields = self.Meta.model._meta.fields

        # Procesar campos directos del modelo
        for field in model_fields:
            if not hasattr(field, 'name'):
                continue
            field_name = field.name

            if isinstance(field, (ForeignKey, OneToOneField)):
                # Siempre construir filtro FK directo
                self.filters[field_name] = SafeFKFilter(
                    field_name=field_name, lookup_expr="exact"
                )

                # Agregamos filtros recursivos para el modelo relacionado
                if self.ENABLE_DEEP_FILTERING:
                    self.add_fk_filters(
                        field,
                        f'{field_name}__',
                        1,
                        self.MAX_FK_DEPTH,
                        requested_filters
                    )
                continue

            # Filtros básicos - construir siempre o según lazy loading
            should_build_basic = (
                not self.LAZY_LOADING or
                requested_filters is None or
                any(req.startswith(field_name) for req in requested_filters)
            )

            if should_build_basic:
                # Filtros generales para cualquier campo
                self.filters[f'{field_name}_in'] = django_filters.BaseInFilter(
                    field_name=field_name,
                    lookup_expr='in'
                )
                self.filters[f'{field_name}_exclude'] = django_filters.BaseInFilter(
                    field_name=field_name,
                    method=self.filter_exclude_field
                )
                self.filters[f'{field_name}_isnull'] = django_filters.BooleanFilter(
                    field_name=field_name,
                    lookup_expr='isnull'
                )

                # Usar el método auxiliar para agregar filtros específicos
                self._add_field_filters(field, field_name)

        # ===== PROCESAMIENTO DE RELACIONES INVERSAS =====
        # AQUÍ ESTÁ LA MEJORA CLAVE PARA TU PROBLEMA
        if self.ENABLE_REVERSE_RELATIONS:
            relations_info = self._get_reverse_relations_info(self.Meta.model)

            for relation_name, relation_info in relations_info.items():
                # Filtro directo para la relación inversa
                relation_field_name = relation_name

                # Verificar si necesitamos construir este filtro
                should_build_relation = (
                    not self.LAZY_LOADING or
                    requested_filters is None or
                    any(req.startswith(relation_field_name)
                        for req in requested_filters)
                )

                if should_build_relation:
                    # Para relaciones one-to-one inversas, agregar filtro directo
                    if relation_info['type'] == 'one_to_one':
                        self.filters[relation_field_name] = SafeFKFilter(
                            field_name=relation_field_name,
                            lookup_expr="exact"
                        )

                        # Agregar filtros isnull para verificar existencia
                        self.filters[f'{relation_field_name}_isnull'] = django_filters.BooleanFilter(
                            field_name=relation_field_name,
                            lookup_expr='isnull'
                        )

                    # Agregar filtros recursivos para el modelo relacionado
                    if self.ENABLE_DEEP_FILTERING:
                        self.add_reverse_relation_filters(
                            relation_info,
                            f'{relation_field_name}__',
                            1,
                            self.MAX_FK_DEPTH,
                            requested_filters
                        )
