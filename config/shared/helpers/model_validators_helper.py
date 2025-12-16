from django.core.exceptions import ValidationError
import re

from config.shared.constants.constants import MONTHS


def string_array_model_validator(array):
    if not isinstance(array, list):
        raise ValidationError("El array debe ser de strings.")

    for elemento in array:
        if not isinstance(elemento, str):
            raise ValidationError("El array debe ser de strings.")
    return True


def moths_array_model_validator(array):
    if not isinstance(array, list):
        raise ValidationError("El array debe ser de strings.")

    for month in array:
        if not isinstance(month, str):
            raise ValidationError("El array debe ser de strings.")
        if month not in MONTHS:
            raise ValidationError(f"El mes '{month}' no es válido.")
    return True


def facturas_promocion_array_validator(array):
    if array is None:
        return True  # optional field

    if not isinstance(array, list):
        raise ValidationError("El array debe ser un array")

    for factura_num in array:
        if not isinstance(factura_num, int):
            raise ValidationError("El array debe ser de enteros")
    return True


def exists_pk_model_validator(pk, Model):
    if not Model.objects.filter(pk=pk).exists():
        raise ValidationError(
            f"No se ha encontrado el registro con el identificador {pk} en {Model.__name__}")


def exists_pk_list_model_validator(pks, Model):
    # is unique pks list
    if len(pks) != len(set(pks)):
        raise ValidationError("Los elementos del array deben ser únicos")

    pks_not_found = []
    found_instances = Model.objects.filter(pk__in=pks)

    len_pks = len(set(pks))
    len_found_instances = len(found_instances)
    if len_pks != len_found_instances:
        pks_not_found = list(
            set(pks) - set(found_instances.values_list('pk', flat=True)))
        raise ValidationError(
            f"No se han encontrado los registros con los identificadores {pks_not_found} en {Model.__name__}")

    return True


def exists_by_code_model_validator(code, Model):
    if not Model.objects.filter(codigo=code).exists():
        raise ValidationError(
            f"No se ha encontrado el registro con el código {code} en {Model.__name__}")


def exist_by_codigo_model_validator(codigo, Model):
    if not Model.objects.filter(codigo=codigo).exists():
        raise ValidationError(
            f"No se ha encontrado el registro con el código {codigo} en {Model.__name__}")


def exists_by_code_list_model_validator(codes, Model):
    string_array_model_validator(codes)

    for code in codes:
        exists_by_code_model_validator(code, Model)


# ### Model validators
def unique_pks_or_all_model_validator(array, Model):
    if not isinstance(array, list):
        raise ValidationError("El array debe ser de enteros")

    # validate unique elements
    if len(array) != len(set(array)):
        raise ValidationError("Los elementos del array deben ser únicos")

    # if is all ignore validation
    if array == ["*"]:
        return True

    # validate if all elements are integers and exist in the model
    for pk in array:
        if not isinstance(pk, int):
            raise ValidationError("El array debe ser de enteros")

        exists_pk_model_validator(pk, Model)


def unique_pks_model_validator(array, Model):
    if not isinstance(array, list):
        raise ValidationError("El array debe ser de enteros")
    # validate unique elements
    if len(array) != len(set(array)):
        raise ValidationError("Los elementos del array deben ser únicos")

    # validate if all elements are integers and exist in the model
    for pk in array:
        if not isinstance(pk, int):
            raise ValidationError("El array debe ser de enteros")

        exists_pk_model_validator(pk, Model)


def unique_codes_model_validator(array, Model):
    if not isinstance(array, list):
        raise ValidationError("El array debe ser de strings")

    # validate array objects has `code` key
    for item in array:
        if 'codigo' not in item:
            raise ValidationError(
                "Cada elemento del array debe tener un campo 'codigo'")

    # validate unique elements by code/codigo
    codes_list = [item['codigo'] for item in array]
    if len(codes_list) != len(set(codes_list)):
        raise ValidationError("Los elementos del array deben ser únicos")

    # validate if all elements are strings and exist in the model
    for code in codes_list:
        if not isinstance(code, str):
            raise ValidationError("El array debe ser de strings")

        exist_by_codigo_model_validator(code, Model)


# ### Other validators
def plan_ration_validator(value):
    pattern = r"^\d+:\d+$"
    if not re.match(pattern, value):
        raise ValidationError(
            "El valor de compartición debe seguir el formato 'n:n' donde n es un número entero.")
    return True


# Validador de JSON general ----------------
def generic_json_validator(json: dict, campos: list):
    """
    Valida un JSON según los campos y tipos que se le pasen.

    Args:
        json (dict): El JSON a validar.
        campos (list): Una lista de tuplas donde cada tupla contiene el nombre del campo y su tipo esperado.

    Returns:
        bool: True si el JSON es válido, de lo contrario lanza una excepción.
    """
    for campo, tipo in campos:
        if campo not in json:
            raise ValidationError(f"El campo '{campo}' es requerido.")
        if not isinstance(json[campo], tipo):
            raise ValidationError(
                f"El campo '{campo}' debe ser de tipo {tipo.__name__}.")
    return True


def ips_array_model_validator(array: list):
    for json in array:
        generic_json_validator(json, [("ip", str), ("available", bool)])
    return True


def ports_array_model_validator(array: list):
    for json in array:
        generic_json_validator(json, [("puerto", str), ("estado", bool)])
