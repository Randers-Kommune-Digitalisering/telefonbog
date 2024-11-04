import urllib.parse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateSchema

from config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_DATABASE, DB_SCHEMA
from models import Base


def get_engine():
    password = urllib.parse.quote_plus(DB_PASS)
    connection_string = f'postgresql+psycopg2://{DB_USER}:{password}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}'
    engine = create_engine(connection_string)
    return engine


engine = get_engine()
Session = sessionmaker(bind=engine)


def get_session():
    session = Session()
    return session


def create_database():
    engine = get_engine()
    with engine.connect() as connection:
        connection.execute(CreateSchema(DB_SCHEMA, if_not_exists=True))
        connection.commit()
    Base.metadata.create_all(engine)
