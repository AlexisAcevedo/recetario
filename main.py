from fastapi import FastAPI
from app.models import models
from app.router import router
from app.config import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(router, prefix="/users", tags=["users"])



#manejar los distintos codigos de error
#devolver user en los response
