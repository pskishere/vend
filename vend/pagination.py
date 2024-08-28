from rest_framework.pagination import PageNumberPagination


class EndPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'pageSize'
    page_query_param = 'current'
