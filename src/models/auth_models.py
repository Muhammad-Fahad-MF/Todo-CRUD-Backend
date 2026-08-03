from pydantic import BaseModel
from sqlmodel import Field 

class SignupReq(BaseModel):
    name: str
    email: str
    password: str

class Login