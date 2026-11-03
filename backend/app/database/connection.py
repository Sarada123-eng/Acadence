from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()

# The project depends on psycopg2-binary; accept the equivalent psycopg URL
# scheme used by the local environment.
database_url = settings.DATABASE_URL.replace("+psycopg", "+psycopg2")
engine = create_engine(database_url, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # Create a new database session

class Base(DeclarativeBase): # Base class for declarative models. We pass this class to the `declarative_base` function to create a new base class for our models.
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()