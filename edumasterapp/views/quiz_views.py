from rest_framework import generics, permissions, filters
from ..serializers.quiz_serializer import QuizSerializer, Quiz
from ..permissions.global_permissions import IsTeacher
from django_filters.rest_framework import DjangoFilterBackend
from service.cache.cache_mixin import CacheMixin


class QuizListCreateAPI(CacheMixin, generics.ListCreateAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher]
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]
    search_fields = ["course_name", "title", "description"]
    ordering_fields = ["time_limit_mins"]
    filterset_fields = {
        "min_score": ["exact", "gte", "lte"],
        "max_score": ["exact", "gte", "lte"],
    }


class QuizDetailAPI(CacheMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

    def perform_destroy(self, instance):
        return instance.delete()
