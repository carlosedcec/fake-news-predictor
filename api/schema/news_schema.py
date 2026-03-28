from pydantic import BaseModel
from typing import Optional, List
from model.news import News

class NewsSchema(BaseModel):
    """ Define como uma nova notícia a ser inserida deve ser representado
    """
    title: str = "Maria"
    text: str = "Maria"

class NewsIdSchema(BaseModel):
    """ Define o parâmetro a ser passado na URL para delete
    """
    news_id: int
