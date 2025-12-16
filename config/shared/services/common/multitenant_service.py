from django.db import connection
from core.multicpy.models import Company


class MultitenantService:

    def get_current_schema(self):
        return connection.schema_name

    def get_current_company(self):
        schema_name = self.get_current_schema()
        return Company.objects.get(schema_name=schema_name)

    def get_current_company_by_schema(self, schema_name: str):
        return Company.objects.get(schema_name=schema_name)
