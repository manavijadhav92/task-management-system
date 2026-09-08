"""
Standard pagination used by all list endpoints.

Wraps DRF's PageNumberPagination but returns results inside the project's
standard {"success": true, "data": {...}} envelope, with pagination
metadata (count, next, previous, page, page_size) alongside the results.
"""

from rest_framework.pagination import PageNumberPagination

from .responses import success_response


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return success_response(
            message="Success",
            data={
                "results": data,
                "count": self.page.paginator.count,
                "num_pages": self.page.paginator.num_pages,
                "current_page": self.page.number,
                "page_size": self.get_page_size(self.request),
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
            },
        )
