from db import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Float, UniqueConstraint


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    hashed_pass = Column(String)


class WalletCurrency(Base):
    __tablename__ = "wallet_currency"

    id = Column(Integer, primary_key=True, index=True)
    user = Column(Integer, ForeignKey(User.id))
    currency = Column(String)
    amount = Column(Float)
    __table_args__ = (UniqueConstraint("user", "currency", name="user_currency"),)
