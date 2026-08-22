# core/exceptions.py
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    # 1. Вызываем дефолтный обработчик DRF
    response = exception_handler(exc, context)

    # Словарь стандартных переводов для статус-кодов
    ru_messages = {
        400: "Invalid request. Please check the submitted data.",
        401: "Authorization error. Please log in.",
        403: "Access denied. You don't have permission.",
        404: "The requested resource was not found.",
        405: "The request method is not supported.",
        429: "Too many requests. Please wait."
    }

    # СЛУЧАЙ 1: Ошибку распознал сам DRF (4xx клиентские ошибки)
    if response is not None:
        message = ru_messages.get(response.status_code, "An error occurred while processing your request.")
        
        # Если есть детальное системное сообщение (например, "No Quiz matches...")
        if isinstance(response.data, dict) and "detail" in response.data:
            message = response.data["detail"]

        # ВАЖНО: Мы отдаем плоскую структуру, БЕЗ двойных конвертов.
        # Рендерер сам положит этот словарь в свой ключ "error"
        response.data = {
            "message": message,
            "details": response.data if response.status_code == 400 else {}
        }
        
        # Удаляем дубликат 'detail', если он остался внутри details
        if isinstance(response.data["details"], dict) and "detail" in response.data["details"]:
            del response.data["details"]["detail"]

        return response

    # СЛУЧАЙ 2: Критическая ошибка (500 Server Error)
    logger.error(f"Критическая ошибка сервера: {exc}", exc_info=True)

    # Возвращаем плоский ответ для рендерера
    return Response(
        {
            "message": "An unexpected error occurred on the server. We are currently working to resolve it.",
            "details": {"server": "Internal Server Error."}
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
