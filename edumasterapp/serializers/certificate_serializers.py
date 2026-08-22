from rest_framework import serializers
from ..models import Certificate


class CertificateSerializer(serializers.ModelSerializer):
    student_fullname = serializers.ReadOnlyField(source="student.full_name")
    course_title = serializers.ReadOnlyField(source="course.title")

    class Meta:
        model = Certificate
        fields = [
            "id",
            "student",
            "student_fullname",
            "course",
            "course_title",
            "certificate_number",
            "image",
            "qr_code",
        ]
