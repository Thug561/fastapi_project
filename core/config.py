import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = 7

origins = [
    "http://localhost:5173",
    "http://localhost:5173/ebook",
    "https://aitishnitsa.github.io",
    "https://aitishnitsa.github.io/ebook",
]
