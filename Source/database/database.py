from sqlalchemy import create_engine
from core.settings import settings
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

engine = create_engine(settings.database_url)
Base = declarative_base()
session = sessionmaker(bind=engine, expire_on_commit=False)

def create_session():
    Base.metadata.create_all(engine)
    return session()
