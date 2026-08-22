from rest_framework import serializers
from django.db import transaction
from ..models import Course, Category


class CourseSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    category = serializers.CharField()

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "category",
            "level",
            "author",
            "price",
            "image",
            "status",
            "duration",
            "total_lessons",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["category"] = (
            instance.category.name if instance.category else None
        )
        return representation

    def validate_title(self, value: str) -> str:
        cleaned_title = value.strip()
        if len(cleaned_title) < 3:
            raise serializers.ValidationError(
                "The course name must contain at least 3 characters."
            )
        return cleaned_title

    def validate_price(self, value) -> float:
        if value <= 0:
            raise serializers.ValidationError(
                "The rate price cannot be negative and must be greater than zero."
            )
        return value

    def validate_duration(self, value: int) -> int:
        if value <= 0:
            raise serializers.ValidationError(
                "The course duration must be greater than 0."
            )
        return value

    @transaction.atomic
    def create(self, validated_data):
        category_name = validated_data.pop("category").strip().capitalize()
        category_obj, _ = Category.objects.get_or_create(name=category_name)
        return Course.objects.create(category=category_obj, **validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        if "category" in validated_data:
            category_name = validated_data.pop("category").strip().capitalize()
            category_obj, _ = Category.objects.get_or_create(name=category_name)
            validated_data["category"] = category_obj
            return super().update(instance, validated_data)
