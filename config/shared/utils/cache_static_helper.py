from django.core.cache import cache


class CacheStaticHelper:

    @staticmethod
    def clear_all_model_cache(model_name: str):
        """
        Borra del cache todas las entradas relacionadas con un modelo específico.
        """
        cache.delete_pattern(f"*{model_name}*")

    @staticmethod
    def clear_all_schema_cache():
        """
        Borra toda la cache general.
        """
        cache.clear()

    @staticmethod
    def clear_all_model_list(name_list: list):
        """
        Borra del cache todas las entradas de una lista de modelos.
        """
        for name in name_list:
            cache.delete_pattern(f"*{name}*")

    @staticmethod
    def clear_all_model_list_cache(name_list: list):
        """
        Borra del cache todas las entradas de una lista de modelos (versión más eficiente).
        """
        cache.delete_many([f"*{name}*" for name in name_list])

    @staticmethod
    def get_cached_value(key: str):
        """
        Obtiene un valor específico del cache.
        """
        return cache.get(key)

    @staticmethod
    def set_cache_value(key: str, value, timeout: int = 3600):
        """
        Guarda un valor en el cache con un timeout opcional (por defecto 1 hora).
        """
        cache.set(key, value, timeout=timeout)
