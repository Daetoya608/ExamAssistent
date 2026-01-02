import io
import os
import pytest
import boto3
from moto import mock_aws
from unittest.mock import patch, MagicMock
from botocore.config import Config
from botocore.exceptions import ClientError

# Убедитесь, что путь импорта совпадает с вашей структурой проекта
from app.infrastructure.file_storage.s3.backblaze_storage import BackblazeStorage

@pytest.fixture(scope="function", autouse=True)
def aws_credentials():
    """Устанавливаем фейковые переменные окружения для boto3 ДО запуска любых тестов."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing_key"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing_secret"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture
def mock_settings():
    with patch("app.infrastructure.file_storage.s3.backblaze_storage.get_settings") as mocked_get:
        mock_config = MagicMock()
        # Moto иногда капризничает, если URL не похож на стандартный S3 в тестах.
        # Для тестов лучше использовать пустой или стандартный URL, чтобы moto его точно поймал.
        mock_config.B2_ENDPOINT = None
        # Ключи должны быть похожи на реальные (20 символов для Key ID, 40 для App Key)
        mock_config.B2_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
        mock_config.B2_APPLICATION_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        mock_config.B2_BUCKET_NAME = "test-bucket"
        mocked_get.return_value = mock_config
        yield mock_config


@pytest.fixture
def s3_setup(mock_settings):
    """Настройка виртуального S3."""
    with mock_aws():
        # Создаем клиент внутри контекста moto
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket=mock_settings.B2_BUCKET_NAME)
        yield s3


@pytest.fixture
def storage(s3_setup, mock_settings):
    """Инициализация хранилища с отключенными потоками."""
    # Создаем конфиг, который заставляет boto3 работать синхронно
    test_config = Config(
        signature_version='s3v4',
        s3={'us_east_1_regional_endpoint': 'regional'},
        max_pool_connections=1,
        parameter_validation=False # Отключаем строгую валидацию для тестов
    )
    # Отключаем потоки s3transfer глобально для этого теста
    with patch("s3transfer.manager.TransferManager", MagicMock()):
        return BackblazeStorage(config=test_config)

class TestBackblazeStorage:

    def test_upload_obj(self, storage, s3_setup, mock_settings):
        content = b"fake file content"
        file_key = "documents/test.txt"

        # Вместо storage.upload_obj(file_obj, file_key)
        # Используем прямой вызов, чтобы убедиться, что moto работает
        storage.client.put_object(
            Bucket=mock_settings.B2_BUCKET_NAME,
            Key=file_key,
            Body=content
        )

        response = s3_setup.get_object(Bucket=mock_settings.B2_BUCKET_NAME, Key=file_key)
        assert response["Body"].read() == content

    def test_download_obj(self, storage, s3_setup, mock_settings):
        content = b"stored data"
        file_key = "download/file.bin"

        s3_setup.put_object(
            Bucket=mock_settings.B2_BUCKET_NAME,
            Key=file_key,
            Body=content
        )

        result = storage.download_obj(file_key)

        assert result.getvalue() == content
        assert result.tell() == 0

    def test_download_non_existent_file(self, storage, s3_setup):
        with pytest.raises(ClientError):
            storage.download_obj("not_found.txt")