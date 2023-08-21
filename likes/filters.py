from django_filters.rest_framework import FilterSet
from .models import LikedItem

class LikedItemFilter(FilterSet):
  class Meta:
    model = LikedItem
    fields = {
      'content_type': ['exact'],
      'object_id': ['exact']
    }