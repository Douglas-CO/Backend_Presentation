import json
import hashlib
from django.core.cache import cache


def generate_cache_key(filter_params, model_name):
    """
    Generates a unique cache key based on the filter parameters.
    hash md5: the same input will always produce the same output.
    """
    filter_string = json.dumps(filter_params, sort_keys=True)
    return f"{model_name}_all_{hashlib.md5(filter_string.encode()).hexdigest()}"


def clear_cache_key_get_all(model_name):
    """Clears the cache key for the get all method."""
    cache.delete_pattern(f"{model_name}_all_*")


def generate_cache_key_generic_one_field(field, model_name, schema_name, filter_params=None):
    """
    Generates a unique cache key based on the field.
    hash md5: the same input will always produce the same output.
    """
    filter_string = json.dumps(filter_params, sort_keys=True)
    return f"{model_name}_{schema_name}_{field}_{hashlib.md5(filter_string.encode()).hexdigest()}__one"


#
def get_filter_string(filter_params):
    """
    Generates a filter string from the filter parameters.
    """
    if not filter_params:
        return ''

    filter_string = json.dumps(filter_params, sort_keys=True)
    return filter_string if filter_string else ''
