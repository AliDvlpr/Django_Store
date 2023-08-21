from rest_framework.pagination import PageNumberPagination

class DefaultPagination(PageNumberPagination):
  page_size = 8

class SmallPagination(PageNumberPagination):
  page_size = 4

class BigPagination(PageNumberPagination):
  page_size = 20