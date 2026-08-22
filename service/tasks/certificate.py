from io import BytesIO
from typing import Tuple
import qrcode
from PIL import Image, ImageDraw, ImageFont

from celery import shared_task
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone

from edumasterapp.models import QuizAttempt, Certificate


@shared_task
def generate_certificate_task(attempt_id: int) -> str:

    attempt = QuizAttempt.objects.select_related(
        'student', 'quiz__course'
    ).get(id=attempt_id)

    student = attempt.student
    course = attempt.quiz.course

    # 1. Гарантия уникальности (идемпотентность)
    certificate, created = Certificate.objects.get_or_create(
        student=student,
        course=course
    )
    if not created:
        return f"Certificate for student {student.id} and course {course.id} already exists. Skipped."

    # 2. Без ошибок в Production: Берём SITE_URL из settings (.env)
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000').rstrip('/')
    verify_url = f"{site_url}/certificate/{certificate.certificate_number}/"

    # 3. Генерация QR-кода
    qr_img = qrcode.make(verify_url)
    qr_io = BytesIO()
    qr_img.save(qr_io, format='PNG')
    qr_file_name = f"qr_{certificate.id}.png"
    certificate.qr_code.save(qr_file_name, ContentFile(qr_io.getvalue()), save=False)

    # 4. Генерация картинки Сертификата (размер 1200x800 px)
    width, height = 1200, 800
    cert_img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(cert_img)

    # Внешняя рамка
    draw.rectangle([20, 20, width - 20, height - 20], outline=(41, 128, 185), width=8)

    # Подгружаем шрифты (или используем стандартный, если системного нет)
    try:
        title_font = ImageFont.truetype("arial.ttf", 46)
        name_font = ImageFont.truetype("arial.ttf", 36)
        text_font = ImageFont.truetype("arial.ttf", 24)
    except IOError:
        title_font = ImageFont.load_default()
        name_font = ImageFont.load_default()
        text_font = ImageFont.load_default()

    # Текст сертификата
    draw.text((width // 2, 120), "СЕРТИФИКАТ ОБ ОКОНЧАНИИ", fill=(41, 128, 185), font=title_font, anchor="mm")
    draw.text((width // 2, 220), "Настоящим подтверждается, что", fill=(100, 100, 100), font=text_font, anchor="mm")

    # Имя студента
    student_name = getattr(student, 'full_name', None) or student.email
    draw.text((width // 2, 300), student_name.upper(), fill=(0, 0, 0), font=name_font, anchor="mm")

    draw.text((width // 2, 380), "успешно завершил(а) курс:", fill=(100, 100, 100), font=text_font, anchor="mm")
    draw.text((width // 2, 440), f"«{course.title}»", fill=(41, 128, 185), font=name_font, anchor="mm")

    # Дата
    date_str = timezone.now().strftime("%d.%m.%Y")
    draw.text((100, 680), f"Дата выдачи: {date_str}", fill=(100, 100, 100), font=text_font)

    cert_no_str = certificate.certificate_number
    draw.text((100, 720), f"Сертификат №: {cert_no_str}", fill=(100, 100, 100), font=text_font)
  

    # 5. Вшиваем QR-код прямо в нижний правый угол сертификата
    qr_resized = qr_img.resize((160, 150))
    cert_img.paste(qr_resized, (width - 250, 600))

    # 6. Сохраняем итоговое изображение сертификата в ImageField
    cert_io = BytesIO()
    cert_img.save(cert_io, format='PNG')
    cert_file_name = f"cert_{certificate.id}.png"
    certificate.image.save(cert_file_name, ContentFile(cert_io.getvalue()), save=True)

    return str(certificate.id)