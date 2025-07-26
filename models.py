from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Product(Base):
    _tablename_ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    category = Column(String)
    price = Column(Integer)
    sold = Column(Integer)

class Order(Base):
    _tablename_ = "orders"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    status = Column(String)

class User(Base):
    _tablename_ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)

class Session(Base):
    _tablename_ = "sessions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)

class Message(Base):
    _tablename_ = "messages"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    sender = Column(String)  
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)