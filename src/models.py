from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

from utils.config import DB_SCHEMA
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

metadata = MetaData(schema=DB_SCHEMA)
Base = declarative_base(metadata=metadata)


class Log(Base):
    __tablename__ = "log"
    id = Column(Integer, primary_key=True, autoincrement=True)
    message = Column(String, nullable=False)
    email = Column(String, nullable=False)
    username = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
