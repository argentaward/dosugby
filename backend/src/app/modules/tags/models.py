from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class TagGroup(Base):
    """Группа тегов = один шаг/фильтр квиза (например, «С кем вы?»)."""

    __tablename__ = "tag_groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True)
    title: Mapped[str] = mapped_column(String(128))
    sort_order: Mapped[int] = mapped_column(default=0)

    tags: Mapped[list["Tag"]] = relationship(
        back_populates="group", order_by="Tag.sort_order", cascade="all, delete-orphan"
    )

    def __str__(self) -> str:
        return self.title


class Tag(Base):
    __tablename__ = "tags"
    __table_args__ = (UniqueConstraint("group_id", "code"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("tag_groups.id", ondelete="CASCADE"))
    code: Mapped[str] = mapped_column(String(32))
    title: Mapped[str] = mapped_column(String(128))
    icon: Mapped[str | None] = mapped_column(String(16))
    sort_order: Mapped[int] = mapped_column(default=0)

    group: Mapped[TagGroup] = relationship(back_populates="tags")

    def __str__(self) -> str:
        return self.title
