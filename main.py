from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from core.config import origins
from api.routes import auth, users
from database.session import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "Welcome to FastAPI modular project!"}
