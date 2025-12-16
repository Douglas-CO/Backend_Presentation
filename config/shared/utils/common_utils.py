import json
import hashlib
from django.core.cache import cache
from django.core.exceptions import ValidationError
import math


# ### REDIS ==========================
def generate_cache_key(filter_params, model_name):
    """Generates a cache key based on the filter parameters."""
    filter_string = json.dumps(filter_params, sort_keys=True)
    return f"{model_name}_all_{hashlib.md5(filter_string.encode()).hexdigest()}"


def clear_cache_key_get_all(model_name):
    """Clears the cache key for the get all method."""
    cache.delete_pattern(f"{model_name}_all_*")


# ### LOCATION ==========================
def get_valid_coords(value: str) -> str:
    """Validates the coordinates."""
    if ',' not in value:
        raise ValidationError("Invalid coordinates, missing comma.")
    lat, lng = value.split(',')
    try:
        float(lat)
        float(lng)
    except ValueError:
        raise ValidationError("Coordinates must be numbers.")
    return value


def calculate_distance_between_coords(coord1_str: str, coord2_str: str) -> float:
    """
    Calcula la distancia entre dos puntos geográficos dados como cadenas de texto
    usando la fórmula del Haversine.

    Args:
    coord1_str (str): Coordenadas del primer punto en formato "lat,lon".
    coord2_str (str): Coordenadas del segundo punto en formato "lat,lon".

    Returns:
    float: La distancia entre los dos puntos en metros.
    """
    valid_coords1_str = get_valid_coords(coord1_str)
    valid_coords2_str = get_valid_coords(coord2_str)

    # Convertir las cadenas a tuplas de flotantes (lat, lon)
    lat1, lon1 = map(float, valid_coords1_str.split(','))
    lat2, lon2 = map(float, valid_coords2_str.split(','))

    # Radio de la Tierra en metros
    R = 6371000

    # Convertir las coordenadas de grados a radianes
    lat1, lon1 = map(math.radians, (lat1, lon1))
    lat2, lon2 = map(math.radians, (lat2, lon2))

    # Diferencia entre las coordenadas
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    # Aplicar la fórmula del Haversine
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * \
        math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distancia en metros
    distance = R * c
    distance = round(distance, 2)

    return distance


# COMMON UTILS ==========================
def humanize_model_name(model_name):
    # Convierte nombres de modelo tipo CamelCase a una forma más legible.
    return ''.join([' ' + char.lower() if char.isupper() else char for char in model_name]).strip().capitalize()


def format_params(params):
    # Convierte el diccionario de parámetros en una lista separada por comas.
    return ', '.join([f"{key} {value}" for key, value in params.items()])
