from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPagination(PageNumberPagination):
    """Переопределение названия параметра пагинации."""

    page_size_query_param = 'limit'
