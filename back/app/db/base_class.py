# app/db/base_class.py

from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr

@as_declarative()
class Base:
    id: Any
    __name__: str

    # Genera automáticamente el nombre de la tabla a partir del nombre de la clase
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()