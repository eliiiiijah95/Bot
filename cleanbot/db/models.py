"""SQLAlchemy ORM models used by the bot."""
from __future__ import annotations

from sqlalchemy import Boolean, Float, Integer, String, TIMESTAMP, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "Customer"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    lastname: Mapped[str | None] = mapped_column(String(100), nullable=True)
    link_to_instagram: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    blog_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    number_of_subscribers: Mapped[int | None] = mapped_column(Integer, nullable=True)
    coverages: Mapped[int | None] = mapped_column(Integer, nullable=True)
    er: Mapped[float | None] = mapped_column(Float, nullable=True)
    link_to_telegram: Mapped[str | None] = mapped_column(String(255), nullable=True)
    link_to_vk: Mapped[str | None] = mapped_column(String(255), nullable=True)
    link_to_youtube: Mapped[str | None] = mapped_column(String(255), nullable=True)
    advertising_formats: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cost_of_advertising_in_stories: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cost_of_advertising_in_a_post: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cost_of_advertising_in_reels: Mapped[int | None] = mapped_column(Integer, nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    profession: Mapped[str] = mapped_column(String(100), nullable=False)
    registered_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, default=func.now())
    time_sub: Mapped[int | None] = mapped_column(Integer, nullable=True)
    category: Mapped[str] = mapped_column(String(25))
    saved_payment_method_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    auto_renewal: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    is_trial_used: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    is_policy_accepted: Mapped[bool | None] = mapped_column(Boolean, nullable=True)


class Access(Base):
    __tablename__ = "Access"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True, nullable=False)
    access_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    time_sub: Mapped[int | None] = mapped_column(Integer, nullable=True)
    saved_payment_method_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    auto_renewal: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
