from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import math


class CustomPagination(PageNumberPagination):
    page_size_query_param = "page_size"
    page_query_param = "page"

    def get_paginated_response(self, data):
        count = self.page.paginator.count
        page_size = self.get_page_size(self.request)
        total_pages = math.ceil(count / page_size) if page_size else 1

        return Response({
            "status": 200,
            "message": "Elementos paginados correctamente",
            "data": {
                "meta": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                    "count": count,
                    "total_pages": total_pages,
                },
                "items": data
            }
        })
