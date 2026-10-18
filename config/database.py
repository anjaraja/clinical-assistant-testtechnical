import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from config.logger import logger

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://clinical_assistant_user:clinical_assistant_password123@db:5432/clinical_assistant_db"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_database_migrations():
    try:
        logger.info("[Database Migration] Checking connection and activate vector.")
        with engine.connect() as connection:
            query = text("CREATE EXTENSION IF NOT EXISTS vector;")
            connection.execute(query)
            connection.commit()
        
        logger.info("[Database Migration] Run migration schema")
        Base.metadata.create_all(bind=engine)
        
        logger.info("[Database Migration] Finish migration schema")
    except Exception as e:
        logger.error(f"[Database Migration] Failed with error: {str(e)}", exc_info=True)
        raise e
