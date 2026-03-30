from model import *
import numpy as np
from tqdm.auto import tqdm

# Instanciação das Classes
loader = Loader()
model = Model()
evaluator = Evaluator()
pipeline = Pipeline()
preprocessor = PreProcessor()

# Carrega dataframe
url_dados = "./ml/data/testdata/test_data.csv"
df = loader.load_data(url_dados)

# Configura X e Y
tqdm.pandas(desc="Preprocessing")
X = df.progress_apply(preprocessor.preprocess_text, axis=1)
y = np.array(df["label"].values, dtype=int)

# Método para testar pipeline de Logistic Regression a partir do arquivo correspondente
def test_modelo_lr():

    # Importando pipeline de Logistic Regression
    lr_path = './ml/pipelines/fake_news_classification_pipeline_lr.pkl'
    rf_model = pipeline.carrega_pipeline(lr_path)

    # Obtendo as métricas de Logistic Regression
    acuracia_rf = evaluator.evaluate(rf_model, X, y)
    
    # Testando as métricas de Logistic Regression
    assert acuracia_rf >= 0.72