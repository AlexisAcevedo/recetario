from fastapi import FastAPI
import models
from router import router
from config import engine
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(CORSMiddleware(allow_origins=["*"], allow_methods=["*"], ))

app.include_router(router, prefix="/users", tags=["users"])



#manejar los distintos codigos de error

