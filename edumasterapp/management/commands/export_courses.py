import csv
from django.core.management.base import BaseCommand
from django.db.models import Count
from edumasterapp.models import Course


class Command(BaseCommand):
    help = "Export all Courses with Lessons count"

    def handle(self, *args, **options):
        filename = "courses_report.csv"

        headers = ["id", "title","status", "price", "Quantity of lesson"]

        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(headers)

            courses = Course.objects.select_related("author").prefetch_related(
                "lessons"
            )

            for course in courses:
                writer.writerow(
                    [
                        course.id,
                        course.title,
                        course.status,
                        course.price,
                        course.total_lessons,  # Вызываем ваше свойство здесь
                    ]
                )

        self.stdout.write(self.style.SUCCESS(f"Отчет {filename} успешно создан!"))
