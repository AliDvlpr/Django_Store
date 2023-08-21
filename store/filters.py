from django_filters.rest_framework import FilterSet
from rest_framework.filters import BaseFilterBackend
from .models import *

class ProductFilter(FilterSet):
  class Meta:
    model = Product
    fields = {
      'group_id': ['exact'],
      'unit_price': ['gt', 'lt']
    }

class GroupFilter(FilterSet):
  class Meta:
    model = Group
    fields = {
      'collection_id': ['exact']
    }

class SupportFilter(FilterSet):
  class Meta:
    model = Support
    fields = {
      'status': ['exact']
    }


class LastStatusFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        last_status = request.query_params.get('last_status', None)
        if last_status:
            queryset = queryset.filter(status__payment_status=last_status).distinct()
        return queryset