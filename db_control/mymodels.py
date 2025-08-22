from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """全モデルのBaseクラス"""
    pass


class Customers(Base):
    __tablename__ = "customers"

    customer_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    customer_name: Mapped[str] = mapped_column(String(100))
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)


class Items(Base):
    __tablename__ = "items"

    item_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    item_name: Mapped[str] = mapped_column(String(100))
    price: Mapped[int] = mapped_column(Integer)


class Purchases(Base):
    __tablename__ = "purchases"

    purchase_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[str] = mapped_column(String(50), ForeignKey("customers.customer_id"))  # ✅ 型を先に
    date: Mapped[datetime] = mapped_column(default=datetime.utcnow)



class PurchaseDetails(Base):
    __tablename__ = "purchase_details"

    purchase_id: Mapped[int] = mapped_column(ForeignKey("purchases.purchase_id"), primary_key=True)
    item_id: Mapped[str] = mapped_column(String(50), ForeignKey("items.item_id"), primary_key=True)  # ✅ 型を先に
    quantity: Mapped[int] = mapped_column(Integer)

