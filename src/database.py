import urllib.parse

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.schema import CreateSchema

from utils.config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_DATABASE, DB_SCHEMA
from models import Base


def get_engine() -> Engine:
    """Create and return a SQLAlchemy engine connected to the PostgreSQL database."""
    password = urllib.parse.quote_plus(DB_PASS)
    connection_string = f'postgresql+psycopg2://{DB_USER}:{password}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}'
    engine = create_engine(connection_string)
    return engine


engine = get_engine()
SessionLocal = sessionmaker(bind=engine)


def get_session() -> Session:
    """Create and return a new SQLAlchemy session."""
    session = SessionLocal()
    return session


def create_database() -> None:
    """Create the database schema and tables if they do not exist."""
    with engine.connect() as connection:
        connection.execute(CreateSchema(DB_SCHEMA, if_not_exists=True))
        connection.commit()
    Base.metadata.create_all(engine)
