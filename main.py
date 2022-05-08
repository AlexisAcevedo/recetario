from fastapi import FastAPI
import models
from router import router
from config import engine
from fastapi.middleware.cors import CORSMiddleware
from fastapi_login import LoginManager


models.Base.metadata.create_all(bind=engine)

app = FastAPI()
origins = [
    "http://localhost.com",
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/users", tags=["users"])