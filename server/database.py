# server/database.py
from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "mysql+pymysql://root:thuong@localhost/devsea"

engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    return Session(engine)
