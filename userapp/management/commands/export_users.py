import csv
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Экспорт пользователей в CSV"

    def handle(self, *args, **options):
        filename = "users.csv"

        # Поля, которые мы берем из базы данных
        fields = ["id", "email", "address", "first_name", "last_name"]

        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            writer.writerow(fields)

            users = User.objects.all().values_list(*fields)
            writer.writerows(users)

            writer.writerow([])

            students = User.objects.filter(role="STUDENT", is_active=True).count() or 0
            writer.writerow(["STUDENTS", students])

            writer.writerow([])

            teachers = User.objects.filter(role="TEACHER", is_active=True).count() or 0
            writer.writerow(["TEACHER", teachers])

            writer.writerow([])

            parents = User.objects.filter(role="PARENT", is_active=True).count() or 0
            writer.writerow(["PARENT", parents])

        self.stdout.write(self.style.SUCCESS(f"Файл {filename} успешно создан!"))
