import io

from app.core.config.utils import get_settings
from app.domains.documents.service import DocumentService
from app.domains.storage.service import StorageService
from app.domains.users.service import UserService
from app.domains.vector_db.service import VectorDBService
from app.domains.documents.schemas import PDFBase, DocumentCreate


class UploadDocumentUseCase:
    def __init__(
            self,
            document_service: DocumentService,
            storage_service: StorageService,
            user_service: UserService,
            vector_db_service: VectorDBService
    ):
        self.document_service = document_service
        self.storage_service = storage_service
        self.user_service = user_service
        self.vector_db_service = vector_db_service


    def _upload_document(self, filename: str, file_obj: io.BytesIO):
        settings = get_settings()
        folder = settings.B2_STANDARD_PATH
        new_file_name = self.document_service.generate_name()

        # Получение чанков из pdf
        file_pdf = self.document_service.parser.get_pdf(file_obj, filename)
        chunks = self.document_service.divide_into_chunks(pdf_model=file_pdf)

        # Сохранение в хранилище
        key = self.storage_service.storage.save(file_obj, new_file_name, folder)

        # Загрузка чанков в векторную базу данных
        self.vector_db_service.vector_storage.upsert_batches(chunks=chunks)

        # Сохранение мета информации в бд
        document_model = DocumentCreate(
            user_id=self.document_service.user_id,
            key=key,
            filename=filename,
        )
        self.document_service.document_repo.create_sync(document_model)


    def execute(self, filename: str, file_obj: io.BytesIO):
        try:
            self._upload_document(
                filename=filename,
                file_obj=file_obj
            )
            return True
        except Exception as e:
            print(f"ERROR!: {e}")
            return False
