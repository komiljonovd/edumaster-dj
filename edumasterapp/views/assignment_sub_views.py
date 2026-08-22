from rest_framework import generics, permissions
from ..serializers.assignment_sub_serializer import (
    AssignmentSubmission,
    StudentAssignmentSerializer,
    TeacherAssignmentSubSerializer,
    AssignmentSubmissionListSerializer,
)
from ..permissions.detail_permissions import (
    IsStudentDetailAssignment,
    IsTeacherDetailAssignment,
)
from ..permissions.global_permissions import IsStudentHasCreation, IsSuperAdmin
from service.cache.cache_mixin import CacheMixin


class StudentCreateAssignmentAPI(CacheMixin, generics.ListCreateAPIView):
    queryset = AssignmentSubmission.objects.filter(is_graded=True).select_related(
        "assignment", "student"
    )
    permission_classes = [
        permissions.IsAuthenticated,
        IsStudentHasCreation | IsSuperAdmin,
    ]

    def get_queryset(self):
        if getattr(self.request.user, "role", None) == "STUDENT":
            return AssignmentSubmission.objects.filter(
                student=self.request.user, is_graded=True
            ).select_related("assignment", "student")

        return AssignmentSubmission.objects.filter(is_graded=True).select_related(
            "assignment", "student"
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return StudentAssignmentSerializer
        return AssignmentSubmissionListSerializer


class StudentUpdateAssignmentAPI(generics.UpdateAPIView):
    queryset = AssignmentSubmission.objects.all()
    serializer_class = StudentAssignmentSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsStudentDetailAssignment | IsSuperAdmin,
    ]


class TeacherAssignmentSubDetailAPI(generics.UpdateAPIView):
    queryset = AssignmentSubmission.objects.all()
    serializer_class = TeacherAssignmentSubSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsTeacherDetailAssignment | IsSuperAdmin,
    ]
