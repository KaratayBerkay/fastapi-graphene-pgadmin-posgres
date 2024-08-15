import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

# from dotenv import load_dotenv
# load_dotenv(".env")

SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres_user:postgres_password@postgresql_db:5432/postgres_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()
