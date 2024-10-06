from pydantic import BaseModel, Field
from config import pwd_context 
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from config import user_role 


class update_account(BaseModel):
    username : str | None = None
    email : str | None = None
    phone_number : int | None = None
    image_url: str | None = None
    
    
class create_user(update_account):
    worker_id : int | None = None
    password : str | None = Field(default=None,min_length=12)

    def hash_password(self):
        self.password = pwd_context.hash(self.password)
        return self


class user_login(OAuth2PasswordRequestForm):

    def verify_password(self,hash_password):
        if pwd_context.verify(self.password, hash_password) == True:
            return True
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")


class update_role(BaseModel):
    accepted:bool
    id:str
    role:user_role


class Token(BaseModel):
    access_token: str 
    token_type: str = "bearer"
    



