import minio

from .. import settings

connection = minio.Minio(
    settings.DATABASES['S3']['HOST'],
    access_key=settings.DATABASES['S3']['ACCESS_KEY'],
    secret_key=settings.DATABASES['S3']['SECRET_KEY'],
    secure=settings.DATABASES['S3']['SECURE'],
)
