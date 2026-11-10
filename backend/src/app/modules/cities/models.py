from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class City(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(128))
    lat: Mapped[float]
    lng: Mapped[float]
    is_active: Mapped[bool] = mapped_column(default=True)

    def __str__(self) -> str:
        return self.name
