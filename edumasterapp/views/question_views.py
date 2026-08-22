from rest_framework import generics, permissions, filters
from ..serializers.question_serializer import Question, QuestionSerializer
from ..permissions.global_permissions import IsTeacher
from django_filters.rest_framework import DjangoFilterBackend
from service.cache.cache_mixin import CacheMixin


class QuestionCreateAPI(generics.CreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["text", "option1", "option2", "option3", "option4"]
    ordering_fields = ["marks"]
    filterset_fields = {
        "correct_answer": ["exact"],
    }


class QuestionDetailAPI(CacheMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

    def perform_destroy(self, instance):
        return instance.delete()
