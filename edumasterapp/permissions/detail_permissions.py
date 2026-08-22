from rest_framework import permissions
from ..models import Assignment, Payment, AssignmentSubmission


class IsStudentDetailAssignment(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if getattr(request.user, "role", None) == "STUDENT":
            course = obj.assignment.lesson.course

            return Payment.objects.filter(
                course=course, student=request.user, status="completed"
            ).exists()


class IsTeacherDetailAssignment(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if getattr(request.user, "role", None) == "TEACHER":
            return obj.assignment.lesson.course.author == request.user

        return False
