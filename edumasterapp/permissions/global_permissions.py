from rest_framework import permissions


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, "role", None) == "SUPER_ADMIN"


class IsSuperAdminHasView(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method == "GET" and getattr(request.user, "role", None) == "STUDENT"
        )


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, "role", None) == "ADMIN"


class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, "role", None) == "TEACHER"


class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method == "GET" and getattr(request.user, "role", None) == "STUDENT"
        )


class IsParent(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method == "GET" and getattr(request.user, "role", None) == "PARENT"
        )


class IsStudentHasCertificate(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if getattr(request.user, "role", None) == "STUDENT":
            return obj.student == request.user


class IsStudentHasPayment(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if getattr(request.user, "role", None) == "STUDENT":
            return obj.student == request.user


class IsStudentHasCreation(permissions.BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, "role", None) == "STUDENT"


