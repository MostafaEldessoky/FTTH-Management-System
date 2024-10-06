from fastapi import APIRouter , Depends , HTTPException , status 
from fastapi.security import OAuth2PasswordBearer 
from models.users import  create_user , Token , user_login , update_account , update_role
from sqlalchemy.orm import  Session 
from sqlalchemy import select
from services.db_services import get_session , users
from services.cache_services import Token_cache , code_verification , forgot_password
from typing import Dict , List
from config import user_role 
from services.cache_services import redis_cache
import random


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/sing_in")

router = APIRouter()


@router.post("/sing_up")
async def sing_up(user:create_user, db_session : Session = Depends(get_session)) -> Dict:
    try:
        user = user.hash_password()
        db_user = users(**user.model_dump())
        db_session.add(db_user)
        db_session.commit()
        return {"message" : "user created"}
    except:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Unique constraint failed")

@router.post("/sing_in")
async def sing_in(user:user_login = Depends(user_login), db_session : Session = Depends(get_session)) -> Token:
    try:
        db_user = db_session.scalar(select(users).where(users.username == user.username))
        if user.verify_password(db_user.password) == True:
            for i in redis_cache.lrange("active_users_pk",0,-1):
                if redis_cache.hget(f":services.cache_services.Token_cache:{i}","id") == db_user.id:
                    redis_cache.delete(f":services.cache_services.Token_cache:{i}")
                    redis_cache.lrem("active_users_pk",0,i)
                if redis_cache.hgetall(f":services.cache_services.Token_cache:{i}") == None:
                    redis_cache.lrem("active_users_pk",0,i)
            token_cache = Token_cache(id = db_user.id, role = db_user.role).save()
            redis_cache.expire(name =f":services.cache_services.Token_cache:{token_cache.pk}", time = token_cache.exp)
            redis_cache.lpush("active_users_pk",token_cache.pk)
            encoded_token = token_cache.create_access_token()
            return Token(access_token = encoded_token)
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

@router.get("/user_info")
async def user_info(token:str = Depends(oauth2_scheme),db_session : Session = Depends(get_session)) -> dict:
    try:
        cache_token = Token_cache.decode_token(token)
        db_user = db_session.scalar(select(users).where(users.id == cache_token["id"]))
        user = {}
        user["worker_id"] = db_user.worker_id
        user["username"] = db_user.username
        user["email"] = db_user.email
        user["image_url"] = db_user.image_url
        user["phone_number"] = db_user.phone_number
        user["role"] = db_user.role
        return user
    except:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Session expired")

@router.get("/email_verification_code{email}")
async def email_verification_code(email : str,db_session : Session = Depends(get_session)) -> Dict :
    try: 
        db_user = db_session.scalar(select(users).where(users.email == email))
        if db_user != None:
            sequence = random.randint(100000,999999)
            code = code_verification(email=db_user.email,code = sequence).save()
            redis_cache.expire(name =f":services.cache_services.code_verification:{code.pk}", time = 60)
            # sendMail(app_mail,db_user.email,"account_verification_code",f"your email verification code is : {sequence}","localhost")
            return {"pk" : code.pk,"code" : code.code}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    except:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="database problem")


@router.put("/forgot_password")
async def forgot_password(new_password : forgot_password, db_session : Session = Depends(get_session)) -> Dict:
    try:
        password = new_password.validate_identity()
        redis_cache.delete(f":services.cache_services.code_verification:{new_password.pk}")
        db_user = db_session.scalar(select(users).where(users.email == new_password.email))
        for i in redis_cache.lrange("active_users_pk",0,-1):
                if redis_cache.hget(f":services.cache_services.Token_cache:{i}","id") == db_user.id:
                    redis_cache.delete(f":services.cache_services.Token_cache:{i}")
        db_user.password = create_user(password = password).hash_password().password
        db_session.add(db_user)
        db_session.commit()
        return {"message" : "password changed"}
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="expired code")
        
        
@router.put("/update_account")
async def update_account(new_user:update_account , token:str = Depends(oauth2_scheme),db_session : Session = Depends(get_session)) -> update_account:
    try: 
        cache_token = Token_cache.decode_token(token)
        db_user = db_session.scalar(select(users).where(users.id == cache_token["id"]))
        if new_user.username != None:
            db_user.username = new_user.username
        if new_user.email != None:
            db_user.email = new_user.email
        if new_user.phone_number != None:
            db_user.phone_number = new_user.phone_number
        if new_user.image_url != None:
            db_user.image_url = new_user.image_url
        db_session.add(db_user)
        db_session.commit()
        return new_user
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")


@router.put("/sign_out")
async def sign_out(token:str = Depends(oauth2_scheme)) -> Dict:
    try:
        cache_token = Token_cache.decode_token(token)
        redis_cache.delete(f":services.cache_services.Token_cache:{cache_token['pk']}")
        redis_cache.lrem("active_users_pk",0,cache_token['pk'])
    except:
        pass
    finally:
        return {"message" : "user signed out"}

@router.post("/request_role{role}")
async def request_role(role:user_role, token:str = Depends(oauth2_scheme)) -> Dict:
    try:
        cache_token = Token_cache.decode_token(token)
        redis_cache.lpush("requested_role",f'{cache_token["id"]}:{role.value}')
        return {"message" : "role requested"}
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="database problem")

@router.get("/roles_requested")
async def roles_requested(token:str = Depends(oauth2_scheme)) :
    try:
        cache_token = Token_cache.decode_token(token)
        if cache_token["role"] == user_role.general_admin.value:
            return redis_cache.lrange("requested_role",0,-1)
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="permission denied")
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
@router.put("/update_role")
async def update_role(update:update_role,token:str = Depends(oauth2_scheme),db_session : Session = Depends(get_session)) -> Dict:
    try:
        cache_token = Token_cache.decode_token(token)
        if cache_token["role"] == user_role.general_admin.value:
            if update.accepted == True:
                db_user = db_session.scalar(select(users).where(users.id == update.id))
                db_user.role = update.role.value
                db_session.add(db_user)
                db_session.commit()
                redis_cache.lrem(name="requested_role",count=0,value=update.id + ":" + update.role.value)
                return {"message" : "role updated"}
            else:
                redis_cache.lrem(name="requested_role",count=0,value=update.id + ":" + update.role.value)
                return {"message" : "role rejected"}
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="permission denied")
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="database problem")
@router.get("/all_users")
async def all_users(token:str = Depends(oauth2_scheme),db_session : Session = Depends(get_session)):
    try:
        cache_token = Token_cache.decode_token(token)
        if cache_token["role"] == user_role.general_admin.value:
            db_users = db_session.scalars(select(users)).all()
            for db_user in db_users:
                del db_user.password
                del db_user.image_url
            return db_users
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="permission denied")
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="database problem")

@router.delete("/delete_account")
async def delete_account(user_id:str,token:str = Depends(oauth2_scheme),db_session : Session = Depends(get_session)) -> Dict:
    try:
        cache_token = Token_cache.decode_token(token)
        if cache_token["role"] == user_role.general_admin.value:
            db_user =db_session.scalar(select(users).where(users.id == user_id))
            db_session.delete(db_user)
            db_session.commit()
            return {"message" : "account deleted"}
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="permission denied")
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="database problem")


