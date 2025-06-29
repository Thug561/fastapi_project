from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# DATABASE_URL = "sqlite:///./test.db"
DATABASE_URL = "postgresql://ebook_db_y7e4_user:0xafHPKtkvidYg7wnRrOcJBOGafJ5SP1@dpg-d0kts17fte5s7390ss50-a:5432/ebook_db_y7e4"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()
