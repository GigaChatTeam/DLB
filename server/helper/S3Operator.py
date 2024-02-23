from datetime import timedelta

import minio
from urllib3.exceptions import MaxRetryError

from . import SQLOperator
from .. import settings

connection: minio.Minio = minio.Minio(
    settings.DATABASES['S3']['HOST'],
    access_key=settings.DATABASES['S3']['ACCESS_KEY'],
    secret_key=settings.DATABASES['S3']['SECRET_KEY'],
    secure=settings.DATABASES['S3']['SECURE'],
)


def get_presign_url(*, bucket, path, expires=timedelta(hours=2)) -> str | None:
    try:
        return connection.get_presigned_url(
            "GET",
            bucket_name=bucket,
            object_name=path,
            expires=expires
        )
    except MaxRetryError:
        return None
