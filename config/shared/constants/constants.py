from drf_yasg import openapi

# ### Custom ======================================

# ## Pagination --------------------
PAGINATION_DEFAULT_PAGE_NUMBER = 1
PAGINATION_DEFAULT_PAGE_SIZE = 10
PAGINATION_PAGE_SIZE_KEY = "page_size"
PAGINATION_PAGE_NUMBER_KEY = "page"


# ### Swagger ======================================
# Parámetros de paginación
page_size_openapi = openapi.Parameter(
    name="page_size",
    in_=openapi.IN_QUERY,
    type=openapi.TYPE_INTEGER,
    required=False,
    description="Page size",
)
page_openapi = openapi.Parameter(
    name="page",
    in_=openapi.IN_QUERY,
    type=openapi.TYPE_INTEGER,
    required=False,
    description="Page number",
)
order_by_openapi = openapi.Parameter(
    name="order_by",
    in_=openapi.IN_QUERY,
    type=openapi.TYPE_STRING,
    required=False,
    description="Campo por el cual se ordenará la consulta",
)
oder_up_openapi = openapi.Parameter(
    name="order_up",
    in_=openapi.IN_QUERY,
    type=openapi.TYPE_BOOLEAN,
    required=False,
    description="Orden ascendente",
)
