from rest_framework import serializers
from ..models import Payment, Course, Status
from django.contrib.auth import get_user_model
from userapp.models import ParentChild
from django.utils import timezone

User = get_user_model()


class PaymentSerializer(serializers.ModelSerializer):
    course_name = serializers.ReadOnlyField(source="course.title")
    student_full_name = serializers.ReadOnlyField(source="student.full_name")

    course_id = serializers.IntegerField(write_only=True)
    student_id = serializers.IntegerField(
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Payment
        fields = (
            "id",
            "course",
            "course_name",
            "course_id",
            "student_id",
            "student",
            "student_full_name",
            "amount",
            "method",
            "status",
            "payment_date",
        )
        read_only_fields = (
            "id",
            "amount",
            "status",
            "payment_date",
            "course",
            "student",
        )

    def validate(self, attrs):
        user = self.context["request"].user
        course_id: int = attrs.get("course_id")
        student_id: int | None = attrs.get("student_id")

        try:
            course = Course.objects.get(
                id=course_id, is_deleted=False, status=Status.ACTIVE
            )
        except Course.DoesNotExist:
            raise serializers.ValidationError(
                {"course_id": "Course not found or not active."}
            )

        role: str = getattr(user, "role", "").upper()
        if role == "STUDENT":
            target_student = user
        elif role == "PARENT":
            if not student_id:
                raise serializers.ValidationError(
                    {"student_id": "Родитель обязан указать ID ребенка."}
                )

            if not ParentChild.objects.filter(
                parent=user, student_id=student_id, is_confirmed=True
            ).exists():
                raise serializers.ValidationError(
                    {"student_id": "No confirmed child with this ID was found."}
                )

            target_student = User.objects.get(id=student_id)
        else:
            raise serializers.ValidationError(
                {"detail": "Insufficient rights to purchase."}
            )

        if Payment.objects.filter(
            student=target_student, course=course, status="completed"
        ).exists():
            raise serializers.ValidationError(
                {"detail": "This course has already been paid for for this student.."}
            )

        attrs["course"] = course
        attrs["target_student"] = target_student
        return attrs

    def create(self, validated_data):
        course = validated_data["course"]
        target_student = validated_data["target_student"]
        payment_method = validated_data.get("method", "card")

        return Payment.objects.create(
            student=target_student,
            course=course,
            amount=course.price,
            method=payment_method,
            status="completed",
            payment_date=timezone.now(),
        )
