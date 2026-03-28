from model import *

# To run: pytest -v test_modelos.py

# Instanciação das Classes
carregador = Carregador()
modelo = Model()
avaliador = Avaliador()
pipeline = Pipeline()

# Parâmetros    
url_dados = "../ml/data/testdata/test_data.csv"

# Carga dos dados
dataset = carregador.carregar_dados(url_dados, colunas)
array = dataset.values
X = array[:,0:-1]
y = array[:,-1]

# Método para testar pipeline Random Forest a partir do arquivo correspondente
def test_modelo_rf():
    # Importando pipeline de Random Forest
    rf_path = './MachineLearning/pipelines/rf_diabetes_pipeline.pkl'
    modelo_rf = pipeline.carrega_pipeline(rf_path)

    # Obtendo as métricas do Random Forest
    acuracia_rf = avaliador.avaliar(modelo_rf, X, y)
    
    # Testando as métricas do Random Forest
    # Modifique as métricas de acordo com seus requisitos
    assert acuracia_rf >= 0.78
    # assert recall_rf >= 0.5 
    # assert precisao_rf >= 0.5 
    # assert f1_rf >= 0.5
    

