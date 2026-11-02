from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()

engine = create_engine(settings.DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # Create a new database session

class Base(DeclarativeBase): # Base class for declarative models. We pass this class to the `declarative_base` function to create a new base class for our models.
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()