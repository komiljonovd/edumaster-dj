from rest_framework import generics, permissions, filters
from ..serializers.payment_serializer import PaymentSerializer, Payment
from ..permissions.global_permissions import (
    IsSuperAdmin,
    IsStudent,
    IsStudentHasPayment,
    IsStudentHasCreation,
)
from django_filters.rest_framework import DjangoFilterBackend
from service.cache.cache_mixin import CacheMixin


class PaymentListCreateAPI(CacheMixin, generics.ListCreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsSuperAdmin | IsStudentHasCreation,
    ]
    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]

    search_fields = ["student_full_name", "course_name", "transaction_id"]
    ordering_fields = ["payment_date"]
    filterset_fields = {
        "status": ["exact"],
        "method": ["exact"],
        "amount": ["exact", "gte", "lte"],
    }

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "role", None) == "STUDENT":
            return Payment.objects.filter(student=user).select_related("student")
        return Payment.objects.select_related("student")


class PaymentDetailAPI(CacheMixin, generics.RetrieveAPIView):
    queryset = Payment.objects.select_related("student")
    serializer_class = PaymentSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsSuperAdmin | IsStudentHasPayment,
    ]
