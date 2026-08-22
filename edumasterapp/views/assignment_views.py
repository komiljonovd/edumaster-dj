from rest_framework import generics, permissions
from ..serializers.assignment_serializer import AssignmentSerializer, Assignment
from ..permissions.global_permissions import IsSuperAdmin, IsAdmin, IsTeacher, IsStudent
from ..permissions.paid_permissions import IsStudentAssignment
from service.cache.cache_mixin import CacheMixin


class AssignmentListCreateAPI(CacheMixin, generics.ListCreateAPIView):
    queryset = Assignment.objects.select_related("lesson")
    serializer_class = AssignmentSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsSuperAdmin | IsAdmin | IsTeacher,
    ]

    def get_queryset(self):
        if getattr(self.request.user, "role", None) == "STUDENT":
            return Assignment.objects.filter()


class AssignmentDetailAPI(CacheMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Assignment.objects.select_related("lesson")
    serializer_class = AssignmentSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsSuperAdmin | IsAdmin | IsTeacher | IsStudentAssignment,
    ]

    def perform_destroy(self, instance):
        return instance.delete()
