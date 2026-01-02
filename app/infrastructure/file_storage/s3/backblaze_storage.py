import os
from typing import IO, Any, BinaryIO, Union
import io

import boto3
from botocore.config import Config
from mypy_boto3_s3 import S3Client

from app.infrastructure.file_storage.utils import get_key
from app.core.config.utils import get_settings
from app.domains.storage.interface import FileStorage


class BackblazeStorage(FileStorage):

    def __init__(self, settings=None, config=None):
        settings = get_settings() if settings is None else settings
        config = Config(signature_version='s3v4') if config is None else config
        self.client: S3Client = boto3.client(
            service_name='s3',
            endpoint_url=settings.B2_ENDPOINT,
            aws_access_key_id=settings.B2_KEY_ID,
            aws_secret_access_key=settings.B2_APPLICATION_KEY,
            config=config
        )
        self._bucket_name = settings.B2_BUCKET_NAME


    def _upload_obj(self, file_obj: IO[Any], key: str) -> None:
        self.client.upload_fileobj(file_obj, self._bucket_name, key)


    def download_obj(self, key: str) -> io.BytesIO:
        temp_obj = io.BytesIO()
        self.client.download_fileobj(self._bucket_name, key, temp_obj)
        temp_obj.seek(0)
        return temp_obj


    def save(
            self,
            file_obj: BinaryIO,
            filename: str,
            folder: str = "",
            content_type: str = "application/octet-stream"
    ) -> str:
        key = get_key(filename, folder)
        self._upload_obj(file_obj, key)
        return key


    def download(self, file_id: str, destination: Union[str, BinaryIO]) -> None:
        if isinstance(destination, str):
            with open(destination, 'wb') as f:
                self.client.download_fileobj(self._bucket_name, file_id, f)
        else:
            self.client.download_fileobj(self._bucket_name, file_id, destination)
            if hasattr(destination, 'seek'):
                destination.seek(0)


    def get_file_bytes(self, file_id: str) -> bytes:
        result = self.download_obj(file_id)
        return result.getvalue()
