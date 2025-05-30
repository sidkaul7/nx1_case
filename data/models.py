from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class Result(Base):
    __tablename__ = 'results'
    id = Column(String, primary_key=True, default=generate_uuid)
    url = Column(String, nullable=True)
    text = Column(Text, nullable=True)
    model_output = Column(SQLiteJSON, nullable=False)
    validation = Column(String, nullable=True)
    expected = Column(SQLiteJSON, nullable=True)
    company = Column(String, nullable=True)
    template = Column(String, nullable=True) 