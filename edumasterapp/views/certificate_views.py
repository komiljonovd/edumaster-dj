from rest_framework import generics, permissions, filters
from ..serializers.certificate_serializers import Certificate, CertificateSerializer
from ..permissions.global_permissions import (
    IsStudentHasCertificate,
    IsSuperAdmin,
    IsStudent,
)
from service.cache.cache_mixin import CacheMixin


class CertificateListAPI(CacheMixin, generics.ListAPIView):
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin | IsStudent]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["certificate_number"]
    ordering_fields = ["issue_date"]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "role", None) == "STUDENT":
            return Certificate.objects.filter(student=user)
        return Certificate.objects.all()


class CertificateDetailAPI(CacheMixin, generics.RetrieveAPIView):
    queryset = Certificate.objects.select_related("course", "student")
    serializer_class = CertificateSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsSuperAdmin | IsStudentHasCertificate,
    ]
    lookup_field = "certificate_number"
