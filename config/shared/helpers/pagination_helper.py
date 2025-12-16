from config.shared.constants.constants import (
    PAGINATION_DEFAULT_PAGE_NUMBER,
    PAGINATION_DEFAULT_PAGE_SIZE,
    PAGINATION_PAGE_SIZE_KEY,
    PAGINATION_PAGE_NUMBER_KEY,
)


def get_pagination_parameters_rest(request):
    filter_params = request.GET

    page_number = request.GET.get(
        PAGINATION_PAGE_NUMBER_KEY, PAGINATION_DEFAULT_PAGE_NUMBER
    )

    page_size = request.GET.get(
        PAGINATION_PAGE_SIZE_KEY, PAGINATION_DEFAULT_PAGE_SIZE
    )

    return filter_params, page_number, page_size
