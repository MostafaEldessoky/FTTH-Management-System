from fastapi import FastAPI
from contextlib import asynccontextmanager
from controllers import users


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    yield


app = FastAPI(lifespan=lifespan)


app.include_router(users.router, prefix="/users", tags=["users"])
