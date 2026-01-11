from abc import ABC, abstractmethod
from typing import BinaryIO, Union


class FileStorage(ABC):

    @abstractmethod
    def save(
            self,
            file_obj: BinaryIO,
            filename: str,
            folder: str = "",
            content_type: str = "application/octet-stream"
    ) -> str:
        """
        Сохраняет файл в хранилище.

        :param file_obj: Поток байтов (file.file из FastAPI или open('...', 'rb'))
        :param filename: Желаемое имя файла (например, 'report.pdf')
        :param folder: Папка или префикс (например, 'users/123/documents')
        :param content_type: MIME-тип (важно для корректного отображения в S3)
        :return: Уникальный ключ файла (Key в S3 или относительный путь на диске)
        """
        pass


    @abstractmethod
    def download(self, file_id: str, destination: Union[str, BinaryIO]) -> None:
        """
        Скачивает файл из хранилища.
        :param file_id: Ключ файла в S3 или путь к файлу.
        :param destination: Путь к локальному файлу (str) или файловый объект (BinaryIO).
        """
        pass


    @abstractmethod
    def get_file_bytes(self, file_id: str) -> bytes:
        """Возвращает содержимое файла в виде байтов."""
        pass
