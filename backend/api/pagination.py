from rest_framework.pagination import PageNumberPagination


class MyPaginator(PageNumberPagination):
    """PageNumberPagination которая ограничивается limit."""
    page_size = 6
    page_size_query_param = 'limit'
