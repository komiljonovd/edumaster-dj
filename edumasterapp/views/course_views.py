from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from ..serializers.course_serializer import Course, CourseSerializer
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from ..permissions.global_permissions import (
    IsSuperAdmin,
    IsAdmin,
    IsTeacher,
    IsStudent,
    IsParent,
)
from service.cache.cache_mixin import CacheMixin


class CourseListCreateAPI(CacheMixin, generics.ListCreateAPIView):
    queryset = Course.objects.select_related("category")
    serializer_class = CourseSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsSuperAdmin | IsAdmin | IsTeacher | IsStudent | IsParent,
    ]

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]
    search_fields = ["title", "description", "category__name"]
    ordering_fields = ["duration"]
    filterset_fields = {
        "status": ["exact"],
    }


class CourseDetailApi(CacheMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsSuperAdmin | IsAdmin | IsTeacher | IsStudent | IsParent,
    ]

    def perform_destroy(self, instance):
        return instance.delete()
