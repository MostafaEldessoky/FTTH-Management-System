from redis_om import get_redis_connection , HashModel 
from config import  cache_url , exp , key,algorithm 
from datetime import timedelta 
import jwt
from fastapi import HTTPException, status
from pydantic import BaseModel , Field

redis_cache = get_redis_connection(url = cache_url)

class Token_cache(HashModel):
    id : str 
    role: str 
    exp: timedelta = timedelta(minutes=exp)
    
    def create_access_token(self):
        to_encode = {"pk":self.pk}
        return jwt.encode(to_encode, key, algorithm=algorithm)
    
    def decode_token(token):
        pk =jwt.decode(token, key, algorithms=[algorithm])["pk"]
        return dict(redis_cache.hgetall(f":services.cache_services.Token_cache:{pk}").items())

    class Meta:
        database = redis_cache
        
    
class code_verification(HashModel):
    email : str
    code : int
    
    class Meta:
        database = redis_cache
        
    
class forgot_password(BaseModel):
    pk : str
    email : str
    code : int
    password : str = Field(min_length=12)
    def validate_identity(self):
        validator = dict(redis_cache.hgetall(f":services.cache_services.code_verification:{self.pk}").items())
        if self.code == int(validator["code"]) and self.email == validator["email"]:
            return self.password
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="expired code")
    