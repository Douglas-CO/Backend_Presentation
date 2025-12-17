class Router:
    """
    Router simple para un proyecto sin tenants.
    Todas las operaciones se hacen en la base de datos 'default'.
    """

    def db_for_read(self, model, **hints):
        return 'default'

    def db_for_write(self, model, **hints):
        return 'default'

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Permitir todas las migraciones solo en 'default'
        return db == 'default'
