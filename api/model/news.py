from sqlalchemy import Column, Integer, String, Text
from model.base import Base

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, unique=True)
    title = Column(String(255), nullable=False)
    text = Column(Text, nullable=False)
    label = Column(Integer, nullable=False)

    def __init__(self, title:str, text:str, label:str):
        self.title = title
        self.text = text
        self.label = label