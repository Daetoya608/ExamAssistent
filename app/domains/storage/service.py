from app.domains.storage.interface import FileStorage


class StorageService:
    def __init__(self, storage: FileStorage):
        self.storage = storage
