from pydantic import BaseModel

class UserInput(BaseModel):
    text: str
