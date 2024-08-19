from pydantic import BaseModel

class Character(BaseModel):
    setting: str
    clothing: str
    accessories: str
    gender: str
    style: str