import json
import numpy as np
from flask import redirect
from flask_openapi3 import OpenAPI, Info, Tag
# from urllib.parse import unquote
from sqlalchemy.exc import IntegrityError

from model import *
# from logger import logger
from schema import *
from flask_cors import CORS

info = Info(title="Minha API", version="1.0.0")
app = OpenAPI(
    __name__, info=info, static_folder="../front", static_url_path="/front"
)
CORS(app)

@app.get("/")
def home():
    return redirect("/front/index.html")

@app.get("/news")
def get_pacientes():
    """Lista todos as notícias cadastradas na base"""

    session = Session()
    news = session.query(News).all()

    if not news:
        return { "news": [] }, 200
    else:
        print(news)
        return {
            "news": [
                {
                    "id": item.id,
                    "title": item.title,
                    "text": item.text,
                    "label": item.label,
                }
                for item in news
            ]
        }, 200

@app.post("/news")
def save_news_and_predict(form: NewsSchema):
    """Adiciona uma nova notícia à base de dados"""

    preprocessor = PreProcessor()
    pipeline = Pipeline()

    title = form.title
    text = form.text

    X_input = [preprocessor.preprocess_text(form)]

    pipeline_path = "./ml/pipelines/fake_news_classification_pipeline.pkl"
    model_pipeline = pipeline.carrega_pipeline(pipeline_path)

    label = int(model_pipeline.predict(X_input)[0])

    news = News(
        title=title,
        text=text,
        label=label
    )

    try:

        session = Session()

        if session.query(News).filter(News.title == form.title).first():
            error_msg = "This news already exists in the database"
            return { "message": error_msg }, 409

        session.add(news)
        session.commit()

        return {
            "news": {
                "id": news.id,
                "title": news.title,
                "text": news.text,
                "label": news.label,
            }
        }, 200

    except Exception as e:
        print(e)
        error_msg = "Não foi possível salvar a notícia"
        return { "message": error_msg }, 400


if __name__ == "__main__":
    app.run(debug=True)
