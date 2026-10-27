# core/storage.py — integración con MinIO (almacenamiento de objetos compatible con S3)
import io
import logging
import uuid
from datetime import timedelta
from functools import lru_cache

from fastapi import HTTPException, UploadFile, status
from minio import Minio
from minio.error import S3Error

from core.config import settings

logger = logging.getLogger(__name__)

# Tipos de imagen permitidos, detectados por su "firma" (magic bytes), no por lo que diga el cliente.
def _detect_image_type(data: bytes) -> tuple[str, str] | None:
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg", "jpg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png", "png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp", "webp"
    return None


@lru_cache
def get_minio_client() -> Minio:
    return Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ROOT_USER,
        secret_key=settings.MINIO_ROOT_PASSWORD,
        secure=settings.MINIO_SECURE,
    )


def ensure_bucket() -> None:
    """Crea el bucket (privado) si no existe. Se llama al arrancar la app."""
    client = get_minio_client()
    if not client.bucket_exists(settings.MINIO_BUCKET):
        client.make_bucket(settings.MINIO_BUCKET)
        logger.info("Bucket '%s' creado en MinIO", settings.MINIO_BUCKET)


def upload_avatar(user_id: int, file: UploadFile) -> str:
    """Valida y sube la foto de perfil. Devuelve el nombre del objeto en MinIO."""
    data = file.file.read(settings.AVATAR_MAX_BYTES + 1)
    if len(data) > settings.AVATAR_MAX_BYTES:
        raise HTTPException(
            413,
            f"La imagen excede {settings.AVATAR_MAX_BYTES // (1024 * 1024)} MB",
        )
    detected = _detect_image_type(data)
    if detected is None:
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Formato no permitido (usa JPEG, PNG o WEBP)"
        )
    content_type, ext = detected

    object_name = f"avatars/{user_id}/{uuid.uuid4().hex}.{ext}"
    try:
        get_minio_client().put_object(
            settings.MINIO_BUCKET,
            object_name,
            io.BytesIO(data),
            length=len(data),
            content_type=content_type,
        )
    except S3Error as exc:
        logger.error("Error subiendo a MinIO: %s", exc)
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Almacenamiento no disponible")
    return object_name


def get_presigned_url(object_name: str) -> str:
    """URL temporal de lectura (el bucket es privado)."""
    return get_minio_client().presigned_get_object(
        settings.MINIO_BUCKET,
        object_name,
        expires=timedelta(minutes=settings.MINIO_URL_EXPIRE_MINUTES),
    )


def delete_object(object_name: str) -> None:
    """Borra un objeto; un fallo aquí no debe romper la petición."""
    try:
        get_minio_client().remove_object(settings.MINIO_BUCKET, object_name)
    except S3Error as exc:
        logger.warning("No se pudo borrar %s de MinIO: %s", object_name, exc)
