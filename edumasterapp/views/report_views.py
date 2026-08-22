from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.contrib.auth import get_user_model
from userapp.models import ParentChild
from ..permissions.global_permissions import IsParent
from ..serializers.report_serializer import ChildDetailReportSerializer
from service.cache.cache_mixin import CacheMixin

User = get_user_model()


class ParentChildrenReportAPIView(CacheMixin, APIView):

    permission_classes = [permissions.IsAuthenticated, IsParent]

    def get(self, request) -> Response:
        parent = request.user

        confirmed_student_ids = ParentChild.objects.filter(
            parent=parent, is_confirmed=True
        ).values_list("student_id", flat=True)

        if not confirmed_student_ids:
            return Response(
                {
                    "detail": "You don't have any confirmed children in the system yet.",
                    "children": [],
                },
                status=status.HTTP_200_OK,
            )

        students = User.objects.filter(id__in=confirmed_student_ids)
        serializer = ChildDetailReportSerializer(students, many=True)

        return Response({"children": serializer.data}, status=status.HTTP_200_OK)
