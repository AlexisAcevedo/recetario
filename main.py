from fastapi import FastAPI
import models
from config import engine
from fastapi.middleware.cors import CORSMiddleware
from login_router import router as login_router
from user_router import router as user_router
from me_router import router as me_router


models.Base.metadata.create_all(bind=engine)
app = FastAPI()
origins = [
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
#ROUTES
app.include_router(me_router, prefix="/me", tags=["me"])
app.include_router(login_router, prefix="/auth", tags=["auth"])
app.include_router(user_router, prefix="/user", tags=["user"])