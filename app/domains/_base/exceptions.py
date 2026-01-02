# Собственные исключения CRUD
class CRUDException(Exception):
    """Общая ошибка операций CRUD."""

    pass


class NotFoundException(CRUDException):
    """Запись не найдена."""

    pass


class CreateFailedException(CRUDException):
    """Не удалось создать запись из-за внутренней ошибки или сбоя БД."""

    pass


class CreateIntegrityException(CRUDException):
    """Нарушено ограничение целостности данных при создании записи (например: уникальность, внешний ключ)."""

    pass


class UpdateFailedException(CRUDException):
    """Не удалось обновить запись."""

    pass


class DeleteFailedException(CRUDException):
    """Не удалось удалить запись."""

    pass
