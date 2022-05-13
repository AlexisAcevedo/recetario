from fastapi import FastAPI
import models
from router import router 
from config import engine
from fastapi.middleware.cors import CORSMiddleware
from login_router import router as login_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
origins = [
        "http://localhost:8080",
        "http://localhost:8000",
        "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/users", tags=["users"])
app.include_router(login_router, prefix="/auth", tags=["auth"])