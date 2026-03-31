from pydantic import BaseModel
from typing import List

class NewsSchema(BaseModel):
    """Defines how a new news item to be inserted should be represented"""
    title: str
    text: str

class NewsIdSchema(BaseModel):
    """Defines the parameter to be passed in the URL for delete"""
    news_id: int

class NewsViewSchema(BaseModel):
    """Defines how a news will be represented"""
    id: int
    title: str
    text: str
    label: bool
    
class NewsListSchema(BaseModel):
    """Defines how a list of news will be returned"""
    news: List[NewsViewSchema]

class NewsRemovedSuccessfulSchema(BaseModel):
    """Defines the return for a news that was successfully removed"""
    message: str