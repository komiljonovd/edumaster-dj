from typing import Dict, Any
from django.db import models
from django.contrib.auth import get_user_model
from ..models import Course, Payment
from userapp.models import Role
from django.utils import timezone

User = get_user_model()


class DashboardRepository:
    """Репозиторий для агрегации данных дашборда из БД."""

    def get_statistics(self) -> Dict[str, Any]:
        return {
            "total_users": User.objects.count() or 0,
            "teachers": User.objects.filter(role="TEACHER").count() or 0,
            "students": User.objects.filter(role="STUDENT").count() or 0,
            "parents": User.objects.filter(role="PARENT").count() or 0,
            "total_courses": Course.everything.count() or 0,
            "active_courses": Course.objects.filter(status='ACTIVE',is_deleted=False).count() or 0,
            "total_sales": Payment.objects.filter(status="completed").count() or 0,
            "revenue": float(
                Payment.objects.aggregate(t=models.Sum("amount"))["t"] or 0.0
            ),
            "uploaded_at":timezone.now(),
        }
