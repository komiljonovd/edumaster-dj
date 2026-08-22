from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from ..serializers.lesson_serializer import Lesson, LessonSerializer
from ..permissions.global_permissions import IsSuperAdmin, IsAdmin, IsTeacher
from ..permissions.paid_permissions import IsStudentPaid
from service.cache.cache_mixin import CacheMixin


class LessonCreateAPI(generics.CreateAPIView):
    queryset = Lesson.objects.select_related("course")
    serializer_class = LessonSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsSuperAdmin | IsAdmin | IsTeacher,
    ]

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["title", "description"]
    ordering_fields = ["duration"]


class LessonDetailAPI(CacheMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.select_related("course")
    serializer_class = LessonSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsSuperAdmin | IsAdmin | IsTeacher | IsStudentPaid,
    ]

    def perform_destroy(self, instance):
        return instance.delete()
