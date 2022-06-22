from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = "postgresql://uewpabkirjaqdo:f12a627b18f3e5fbee615a392999800719e7c035e4cf15a97087e88f857ef241@ec2-3-229-252-6.compute-1.amazonaws.com:5432/d6tk9hncqqfjmv"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()