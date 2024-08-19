from pydantic import BaseModel, Field

class Summary(BaseModel):
    title: str
    summary: str