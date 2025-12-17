from django_tenants.utils import schema_context, get_tenant_model
from django.db import connection


class MultitenantStaticHelper:

    @staticmethod
    def get_current_schema():
        return connection.schema_name

    @staticmethod
    def get_current_company():
        schema_name = MultitenantStaticHelper.get_current_schema()
        return print(schema_name=schema_name)

    # ---------------------------------
    @staticmethod
    def excute_callback_in_current_schema(callback, schema_name=None):
        """ All async tasks should send the schema name to this method """
        schema_name = MultitenantStaticHelper.get_current_schema(
        ) if schema_name is None else schema_name
        with schema_context(schema_name):
            return callback()

    # ---------------------------------
    @staticmethod
    def run_in_all_schemas_but_list(callback, exclude_schemas=None):
        if exclude_schemas is None:
            exclude_schemas = ['public',]
        TenantModel = get_tenant_model()
        tenants = TenantModel.objects.exclude(schema_name__in=exclude_schemas)

        for tenant in tenants:
            schema = tenant.schema_name
            with schema_context(schema):
                callback(schema)

    # ---------------------------------
    @staticmethod
    def get_schema_name_from_request(request):
        if hasattr(request, 'tenant'):
            return request.tenant.schema_name
        return MultitenantStaticHelper.get_current_schema()
