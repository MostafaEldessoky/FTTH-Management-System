from fastapi import FastAPI
from contextlib import asynccontextmanager
from controllers import users
from services.db_services import db_init


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_init()
    yield


app = FastAPI(lifespan=lifespan)


app.include_router(users.router, prefix="/users", tags=["users"])
