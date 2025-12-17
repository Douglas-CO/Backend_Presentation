from django.db import connection


class MultitenantService:

    def get_current_schema(self):
        return connection.schema_name

    def get_current_company(self):
        schema_name = self.get_current_schema()
        return print(schema_name=schema_name)

    def get_current_company_by_schema(self, schema_name: str):
        return print(schema_name=schema_name)
