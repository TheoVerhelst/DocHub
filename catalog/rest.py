from rest_framework import viewsets
from rest_framework_extensions.mixins import DetailSerializerMixin

from catalog.serializers import (
    GroupSerializer,
    ShortGroupSerializer,
    CategorySerializer,
    ShortCategorySerializer
)
from catalog.models import Group, Category


class GroupViewSet(DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.prefetch_related(
        "document_set",
        "document_set__user",
        "document_set__tags"
    )
    serializer_class = ShortGroupSerializer
    serializer_detail_class = GroupSerializer

    lookup_field = 'slug'


class CategoryViewSet(DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_detail_class = CategorySerializer
    serializer_class = ShortCategorySerializer
