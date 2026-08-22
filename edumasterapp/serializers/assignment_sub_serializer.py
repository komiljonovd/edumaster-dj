from rest_framework import serializers
from ..models import AssignmentSubmission, Payment
import os
from django.utils import timezone


class StudentAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentSubmission
        fields = ["id", "assignment", "student", "file", "student_comment"]

    def validate_student_comment(self, value: str) -> str:
        comment = value.strip()

        if not comment:
            raise serializers.ValidationError({"Comment can not be empty."})
        return comment

    def validate(self, attrs: dict) -> dict:
        assignment = attrs.get("assignment")
        request = self.context.get("request")
        student = attrs.get("student") or (request.user if request else None)
        course = assignment.lesson.course
        print(student)
        print(course)

        if not Payment.objects.filter(
            course=course, student=student, status="completed"
        ).exists():

            raise serializers.ValidationError(
                {"student": "You can not perform this action."}
            )
        if assignment and assignment.deadline:
            if timezone.now() > assignment.deadline:
                raise serializers.ValidationError(
                    {
                        "deadline": "This assignment is expired. Submission is prohibited."
                    }
                )

        if request and request.method == "POST":
            if AssignmentSubmission.objects.filter(
                assignment=assignment, student=student
            ).exists():
                raise serializers.ValidationError(
                    {
                        "assignment": "You have already submitted a solution for this task. Use the editing feature to change your answer."
                    }
                )

        return attrs


class TeacherAssignmentSubSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentSubmission
        fields = ["id", "score", "teacher_comment", "is_graded"]

    def validate_score(self, value: float) -> float:
        if value is not None and value < 0:
            raise serializers.ValidationError("The score cannot be negative.")
        return value

    def validate_teacher_comment(self, value: str) -> str:
        comment = value.strip()

        if not comment:
            raise serializers.ValidationError({"Comment can not be empty."})
        return comment

    def validate(self, attrs: dict) -> dict:
        score = attrs.get("score")

        if self.instance and score is not None:
            max_score = self.instance.assignment.max_score
            if score > max_score:
                raise serializers.ValidationError(
                    {
                        "score": f"The score given ({score}) exceeds the maximum score for this assignment ({max_score})."
                    }
                )

        return attrs

    def update(self, instance, validated_data: dict):
        if "score" in validated_data or "teacher_comment" in validated_data:
            validated_data["is_graded"] = True

        return super().update(instance, validated_data)


class AssignmentSubmissionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentSubmission
        fields = [
            "id",
            "assignment",
            "student",
            "file",
            "score",
            "student_comment",
            "teacher_comment",
            "is_graded",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["assignment"] = (
            instance.assignment.title if instance.assignment else None
        )

        representation["student"] = instance.student.email if instance.student else None

        return representation
