from flask import redirect
from flask_openapi3 import OpenAPI, Info, Tag

from model import *
from schema import *
from flask_cors import CORS

info = Info(title="Fake News Predictor", version="1.0.0")
app = OpenAPI(__name__, info=info, static_folder="../front", static_url_path="/front")
CORS(app)

home_tag = Tag(
    name="Home",
    description="Home page",
)
docs_tag = Tag(
    name="Documentation",
    description="Documentation selection",
)
news_tag = Tag(
    name="News",
    description="Addition, visualization, removal and prediction of news",
)

@app.get("/", tags=[home_tag])
def home():
    return redirect("/front/index.html")

@app.get("/docs", tags=[docs_tag])
def docs():
    return redirect("/openapi")

@app.get(
    "/news",
    tags=[news_tag],
    responses={"200": NewsListSchema, "404": ErrorSchema},
)
def get_news():
    """Lists all news registered in the database"""

    try:

        session = Session()
        news = session.query(News).all()

        if not news:
            return { "news": [] }, 200
        else:
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

    except Exception as e:
        print(str(e))
        session.rollback()
        return { "message": "Error trying to get the news on the database" }, 400
    finally:
        session.close()

@app.post(
    "/news",
    tags=[news_tag],
    responses={"200": NewsViewSchema, "404": ErrorSchema},
)
def save_news_and_predict(form: NewsSchema):
    """Adds a new news to the database"""

    preprocessor = PreProcessor()
    pipeline = Pipeline()

    title = form.title
    text = form.text

    if not title:
        error_msg = "Title field is required"
        return { "message": error_msg }, 422

    if not text:
        error_msg = "Text field is required"
        return { "message": error_msg }, 422

    if len(text) < 300:
        error_msg = "The news text must be at least 300 characters long"
        return { "message": error_msg }, 422

    X_input = [preprocessor.preprocess_text(form)]

    pipeline_path = "./ml/pipelines/fake_news_classification_pipeline_lr.pkl"
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
            "id": news.id,
            "title": news.title,
            "text": news.text,
            "label": news.label
        }, 200

    except Exception as e:
        print(e)
        session.rollback()
        return { "message": "Error trying to save the news on the database" }, 400
    finally:
        session.close()

@app.delete(
    "/news/<int:news_id>",
    tags=[news_tag],
    responses={"200": NewsRemovedSuccessfulSchema, "404": ErrorSchema},
)
def delete_news(path: NewsIdSchema):
    """Remove a news from the database using the id"""

    try:

        session = Session()

        news = (
            session.query(News)
            .filter(News.id == path.news_id).first()
        )

        if not news:
            return { "message": "News item not found in the database" }, 404
        else:
            session.delete(news)
            session.commit()
            return { "message": "News removed successfully" }, 200

    except Exception as e:
        print(e)
        session.rollback()
        return { "message": "Error trying to delete the news on the database" }, 400
    finally:
        session.close()

if __name__ == "__main__":
    app.run(debug=True)
