from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func

from database import Base
from datetime import datetime



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="customer", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    description = Column(String(500), nullable=True)
    price = Column(Integer, nullable=False)
    category = Column(String(100), nullable=False)
    stock = Column(Integer, default=0, nullable=False)

class Cart(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, default=1, nullable=False)

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    total_amount = Column(Integer, nullable=False)
    status = Column(String(50), default="PLACED", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    status = Column(String, default="PENDING")
    transaction_id = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)