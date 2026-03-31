from model import *
import numpy as np
from tqdm.auto import tqdm

# Classes instanciation
loader = Loader()
model = Model()
evaluator = Evaluator()
pipeline = Pipeline()
preprocessor = PreProcessor()

# Loads dataset
url_dados = "./ml/data/testdata/test_data.csv"
df = loader.load_data(url_dados)

# X and Y configuration
tqdm.pandas(desc="Preprocessing")
X = df.progress_apply(preprocessor.preprocess_text, axis=1)
y = np.array(df["label"].values, dtype=int)

# Method for testing a Logistic Regression pipeline from the corresponding file
def test_modelo_lr():

    # Imports the pipeline
    lr_path = './ml/pipelines/fake_news_classification_pipeline_lr.pkl'
    rf_model = pipeline.carrega_pipeline(lr_path)

    # Get the results metrics
    acuracia_rf = evaluator.evaluate(rf_model, X, y)
    
    # Tests the metrics rate
    assert acuracia_rf >= 0.72