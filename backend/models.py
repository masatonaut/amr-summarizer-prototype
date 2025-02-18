from pydantic import BaseModel

class TextInput(BaseModel):
    summary: str
    article: str

