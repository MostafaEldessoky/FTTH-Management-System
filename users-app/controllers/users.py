from fastapi import APIRouter
from typing import List
from models.users import user, token

router = APIRouter()


@router.post("/sing_up")
async def sing_up() -> token:
    pass


@router.post("/sing_in")
async def sing_in() -> token:
    pass


@router.put("/sign_out")
async def sign_out() -> token:
    pass


@router.put("/change_password")
async def change_password() -> token:
    pass


@router.delete("/delete_me")
async def delete_me() -> user:
    pass


@router.get("/get_active_users")
async def get_active_users() -> List[user]:
    pass


@router.get("/get_all_users")
async def get_all_users() -> List[user]:
    pass


@router.delete("/delete_user")
async def delete_user() -> user:
    pass
