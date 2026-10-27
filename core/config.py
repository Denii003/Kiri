from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Base de datos (si no se define, usa SQLite local para desarrollo)
    DATABASE_URL: str = "sqlite:///./kiri.db"

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # MinIO
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_BUCKET: str = "kiri"
    MINIO_SECURE: bool = False
    MINIO_URL_EXPIRE_MINUTES: int = 15      # vigencia de los enlaces firmados
    AVATAR_MAX_BYTES: int = 2 * 1024 * 1024  # 2 MB

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
