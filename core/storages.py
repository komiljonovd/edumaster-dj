# core/storages.py
import os
from storages.backends.s3 import S3Storage


class PublicMediaStorage(S3Storage):
    """
    Обложки курсов (Course.image), сертификаты (Certificate.image, qr_code).
    Доступ: анонимное чтение, прямая постоянная ссылка.
    """
    bucket_name = os.environ.get("MINIO_PUBLIC_BUCKET", "edumaster-public")
    endpoint_url = os.environ.get("MINIO_ENDPOINT", "http://localhost:9000")
    access_key = os.environ.get("MINIO_APP_USER")
    secret_key = os.environ.get("MINIO_APP_PASSWORD")
    region_name = os.environ.get('MINIOR_REGION')
    addressing_style = "path"         
    default_acl = None
    querystring_auth = True           
    file_overwrite = False


class PrivateDocumentStorage(S3Storage):
    """
    PDF уроков (Lesson.pdf), работы студентов (AssignmentSubmission.file).
    Доступ: только по временной presigned-ссылке.
    """
    bucket_name = os.environ.get("MINIO_PRIVATE_BUCKET", "edumaster-private")
    endpoint_url = os.environ.get("MINIO_ENDPOINT", "http://localhost:9000")
    access_key = os.environ.get("MINIO_APP_USER")
    secret_key = os.environ.get("MINIO_APP_PASSWORD")
    region_name = os.environ.get('MINIOR_REGION')
    addressing_style = "path"
    default_acl = None
    querystring_auth = True
    querystring_expire = 900           
    file_overwrite = False


class PrivateVideoStorage(S3Storage):
    """
    Видео уроков (Lesson.video) — самый чувствительный контент.
    Доступ: только по короткоживущей presigned-ссылке, выдаётся через отдельный API.
    """
    bucket_name = os.environ.get("MINIO_PRIVATE_BUCKET", "edumaster-private")
    endpoint_url = os.environ.get("MINIO_ENDPOINT", "http://localhost:9000")
    access_key = os.environ.get("MINIO_APP_USER")
    secret_key = os.environ.get("MINIO_APP_PASSWORD")
    region_name = os.environ.get('MINIOR_REGION')
    addressing_style = "path"
    default_acl = None
    querystring_auth = True
    querystring_expire = 900           
    file_overwrite = False

    