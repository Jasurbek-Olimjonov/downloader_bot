from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from database.base import BaseModel


class User(BaseModel):
    lan_code: Mapped[str] = mapped_column(String, nullable=True)
