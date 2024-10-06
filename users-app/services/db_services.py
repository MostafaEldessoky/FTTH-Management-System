from sqlalchemy import create_engine   
from sqlalchemy.orm import sessionmaker , Mapped , mapped_column
from sqlalchemy.ext.declarative import declarative_base
import uuid 
from config import  db_url , user_role


engine = create_engine(url = db_url)

Base = declarative_base()

Session = sessionmaker(bind = engine)

def db_init():
    Base.metadata.create_all(bind = engine)
    

def get_session():
    with Session() as session:
        yield session


class users(Base):    
    __tablename__ = "users"
    id : Mapped[str] = mapped_column(primary_key=True, default = uuid.uuid4().hex)
    role : Mapped[str] =mapped_column( default = user_role.base.value)
    worker_id : Mapped[int]  =mapped_column( nullable = False, unique = True)
    username:Mapped[str] =mapped_column( nullable = False, unique = True)
    email:Mapped[str] =mapped_column( nullable = False, unique = True)
    password:Mapped[str] =mapped_column(nullable = False)
    phone_number : Mapped[int] =mapped_column( nullable = False, unique = True)
    image_url: Mapped[str | None] =mapped_column( nullable = True)


    class Config:
        orm_mode = True
