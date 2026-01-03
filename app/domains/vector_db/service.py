from app.domains.vector_db.vector_db_interface import VectorDBInterface


class VectorDBService:
    def __init__(self, vector_storage: VectorDBInterface):
        self.vector_storage = vector_storage
