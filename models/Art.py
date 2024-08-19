from pydantic import BaseModel, Field

class Art(BaseModel):
    title: str
    artist: str
    year_created: int
    style: str