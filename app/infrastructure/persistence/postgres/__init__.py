from datetime import UTC, datetime

from sqlalchemy import TIMESTAMP, Date, Enum, Integer, MetaData, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

convention = {
    "all_column_names": lambda constraint, table: "_".join(
        [str(column.name) for column in constraint.columns.values()]
    ),
    "ix": "ix__%(table_name)s__%(all_column_names)s",
    "uq": "uq__%(table_name)s__%(all_column_names)s",
    "ck": "ck__%(table_name)s__%(constraint_name)s",
    "fk": ("fk__%(table_name)s__%(all_column_names)s__%(referred_table_name)s"),
    "pk": "pk__%(table_name)s",
}

metadata = MetaData(naming_convention=convention)  # type: ignore[arg-type]


class Base(DeclarativeBase):
    metadata = metadata


__all__ = [
    "DeclarativeBase",
    "Base",
]
