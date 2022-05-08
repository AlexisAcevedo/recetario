
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from config import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    password = Column(String)
    name = Column(String)
    lastname = Column(String)