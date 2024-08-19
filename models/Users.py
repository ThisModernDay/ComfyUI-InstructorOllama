from pydantic import BaseModel, Field
from typing import List

class User(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    address: str

class Users(BaseModel):
    users: List[User]