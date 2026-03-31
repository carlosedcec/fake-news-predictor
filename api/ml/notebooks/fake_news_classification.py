# ==============================
# 1. IMPORTS
# ==============================

# Configuração para não exibir os warnings
import warnings
warnings.filterwarnings("ignore")

# Imports gerais
import re
import numpy as np
import pandas as pd
from pickle import dump

# Imports do scikit-learn
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MaxAbsScaler
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report, confusion_matrix

# Bibliotecas para manipulação de texto e NLP
import nltk
from tqdm.auto import tqdm
from nltk.corpus import stopwords

# Bloco de configuração inicial do NLTK
nltk.download("punkt")
nltk.download("stopwords")
nltk.download("wordnet")
nltk.download("omw-1.4")

# ==============================
# 2. LOADING DATA
# ==============================

# Função que configura e padroniza os diferentes csvs, retornando um data frame
def create_data_frame_from_files(datasets):

    # Leitura e concatenação dos data frames
    dfs = []
    for url in datasets:
        print(f"Loading {url}")
        d = pd.read_csv(url, sep=None, engine="python", encoding="utf-8")
        d.columns = d.columns.str.strip().str.lower()
        dfs.append(d)
    df = pd.concat(dfs, ignore_index=True)

    # Normaliza as colunas do dataframe
    for col in ["title", "text", "label"]:
        if col not in df.columns:
            df[col] = np.nan if col != "text" else ""

    # Confiura o título e a label
    df["combined_text"] = df["title"].fillna("") + " " + df["text"].fillna("")
    df["label"] = (df["label"].astype(str).map({ "real": 1, "fake": 0, "1": 1, "0": 0 }))

    # Finaliza o data frame e dropa colunas nulas
    df = df[["combined_text", "label"]]
    df = df.dropna(subset=["combined_text", "label"])

    return df

# Links dos datasets
datasets = [
    'https://raw.githubusercontent.com/carlosedcec/fake-news-predictor/refs/heads/master/api/ml/data/aadyasingh55-fake-news-classification/evaluation.csv',
    'https://raw.githubusercontent.com/carlosedcec/fake-news-predictor/refs/heads/master/api/ml/data/aadyasingh55-fake-news-classification/test%20(1).csv',
    'https://raw.githubusercontent.com/carlosedcec/fake-news-predictor/refs/heads/master/api/ml/data/aadyasingh55-fake-news-classification/train%20(2).csv'
]

print("Loading data...")
df = create_data_frame_from_files(datasets)
print("Data loaded!\n")

# ==============================
# 3. PREPROCESSING DATA
# ==============================

# Função para pré-processar o texto
def preprocess_text(row) -> str:
    """
    Função completa para limpar e pré-processar um único documento de texto.
    Aplica todos os passos da proposta: remoção de metadados, lowering,
    remoção de pontuação/números, tokenização e remoção de stopwords.
    """

    text = row["combined_text"]

    def sanitize_text(text):
        text = re.sub(r"--.*", "", text, flags=re.DOTALL) # Remove assinaturas (começando com '-- ')
        text = re.sub(r">.*", "", text) # Remove linhas de citação (começando com '>')
        text = re.sub(r"\S*@\S*\s?", "", text) # Remove emails
        text = re.sub(r"\s+", " ", text).strip() # Remove quebras de linha e tabs
        text = text.lower()
        return text

    text = sanitize_text(text)

    tokens = text.split()

    stop_words = set(stopwords.words("english"))

    clean_tokens = [
        token
        for token in tokens
        if token not in stop_words
        and len(token) > 2  # Remove stopwords e tokens muito curtos
    ]

    return " ".join(clean_tokens)

tqdm.pandas(desc="Preprocessing")

print("Preprocessing text...")
X = df.progress_apply(preprocess_text, axis=1)
print("Text preprocessed!\n")
y = np.array(df["label"].values, dtype=int)

# ==============================
# 4. TRAIN/TEST SPLIT
# ==============================

# Seta variáveis de configuração
SEED = 7
TEST_SIZE = 0.20
SCORING = 'f1_macro'
NUM_PARTICOES = 5

# Separa dados em treino e teste com estratificação
print("Splitting data into train and test...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=TEST_SIZE, shuffle=True, random_state=SEED, stratify=y
)
print("Data splitted!\n")

print(f"Training set: {X_train.shape[0]} samples")
print(f"Test set: {X_test.shape[0]} samples\n")

# ==============================
# 5. MODEL AVALIATION
# ==============================

# Algoritmos que serão utilizados
knn = ('KNN', KNeighborsClassifier())
random_forest = ('RF', RandomForestClassifier(random_state=SEED))
naive_bayes = ('NB', MultinomialNB())
logistic_regression = ('LogisticREG', LogisticRegression(max_iter=1000))

# tfid pipeline
tfidf = ('tfidf', TfidfVectorizer(min_df=2, max_df=0.9))

# Lista que armazenará os modelos
models = []

# Criando os modelos e adicionando-os na lista de modelos
models.append(('KNN', Pipeline([tfidf, knn])))
models.append(('RF', Pipeline([tfidf, random_forest])))
models.append(('NB', Pipeline([tfidf, naive_bayes])))
models.append(('LogisticREG', Pipeline([tfidf, logistic_regression])))

# Listas para armazenar os resultados
names = []
results = []

# Fold e Estratificação
kfold = StratifiedKFold(n_splits=NUM_PARTICOES, shuffle=True, random_state=SEED)

print("Avaliating algorithms...")

# Avaliação dos modelos
# for name, model in models:
#     cv_results = cross_val_score(model, X_train, y_train, cv=kfold, scoring=SCORING)
#     names.append(name)
#     results.append(cv_results)
#     msg = "%s: %.3f (%.3f)" % (name, cv_results.mean(), cv_results.std())
#     print(msg)

# ==============================
# 6. MODEL AVALIATION WITH SCALER
# ==============================

# Listas para armazenar os resultados
names = []
results = []

# Lista que armazenará as pipelines
pipelines = []

# Transformações que serão utilizadas
standard_scaler = ('StandardScaler', StandardScaler(with_mean=False))
min_max_scaler = ('MinMaxScaler', MaxAbsScaler())

# Dataset original
pipelines.append(('KNN-orig', Pipeline([tfidf, knn])))
pipelines.append(('RF-orig', Pipeline([tfidf, random_forest])))
pipelines.append(('NB-orig', Pipeline([tfidf, naive_bayes])))
pipelines.append(('LogisticREG-orig', Pipeline([tfidf, logistic_regression])))

# Dataset Padronizado
pipelines.append(('KNN-padr', Pipeline([tfidf, standard_scaler, knn])))
pipelines.append(('RF-padr', Pipeline([tfidf, standard_scaler, random_forest])))
pipelines.append(('NB-padr', Pipeline([tfidf, standard_scaler, naive_bayes])))
pipelines.append(('LogisticREG-padr', Pipeline([tfidf, standard_scaler, logistic_regression])))

# Dataset Normalizado
pipelines.append(('KNN-norm', Pipeline([tfidf, min_max_scaler, knn])))
pipelines.append(('RF-norm', Pipeline([tfidf, min_max_scaler, random_forest])))
pipelines.append(('NB-norm', Pipeline([tfidf, min_max_scaler, naive_bayes])))
pipelines.append(('LogisticREG-norm', Pipeline([tfidf, min_max_scaler, logistic_regression])))

print("\nAvaliating algorihtms with scaled data...")

# Executando os pipelines
# for name, model in pipelines:
#     cv_results = cross_val_score(model, X_train, y_train, cv=kfold, scoring=SCORING, n_jobs=4)
#     names.append(name)
#     results.append(cv_results)
#     msg = "%s: %.3f (%.3f)" % (name, cv_results.mean(), cv_results.std())
#     print(msg)

# ==============================
# 7. HIPERPARAMETERS OPTIMIZATION
# ==============================

print("\nOptimizing hiperparameters...")

# Testando otimização de hiperparâmetros da Random Forest
random_forest_pipelines = []
random_forest_pipelines.append(('rf-orig', Pipeline([tfidf, random_forest])))
random_forest_pipelines.append(('rf-padr', Pipeline([tfidf, standard_scaler, random_forest])))
random_forest_pipelines.append(('rf-norm', Pipeline([tfidf, min_max_scaler, random_forest])))

param_grid = [
    {
        'RF__n_estimators': [100, 200],
        'RF__max_depth': [None, 10, 30],
        'RF__min_samples_split': [2, 5],
        'RF__min_samples_leaf': [1, 2]
    }
]

# for name, model in random_forest_pipelines:
#     grid = GridSearchCV(estimator=model, param_grid=param_grid, scoring=SCORING, cv=kfold, n_jobs=4)
#     grid.fit(X_train, y_train)
#     msg = "Sem tratamento de missings: %s - Melhor: %f usando %s" % (name, grid.best_score_, grid.best_params_)
#     print(msg)

# Testando otimização de hiperparâmetros da Logistic Regression
logistic_reg_pipelines = []
logistic_reg_pipelines.append(('logistic_reg-orig', Pipeline([tfidf, logistic_regression])))
logistic_reg_pipelines.append(('logistic_reg-padr', Pipeline([tfidf, standard_scaler, logistic_regression])))
logistic_reg_pipelines.append(('logistic_reg-norm', Pipeline([tfidf, min_max_scaler, logistic_regression])))

param_grid = [
    {
        'LogisticREG__l1_ratio': [0],
        'LogisticREG__solver': ['lbfgs', 'liblinear', 'saga'],
        'LogisticREG__C': [0.1, 1, 10],
        'LogisticREG__tol': [1e-4, 1e-3]
    },
    {
        'LogisticREG__l1_ratio': [1],
        'LogisticREG__solver': ['liblinear', 'saga'],
        'LogisticREG__C': [0.1, 1, 10],
        'LogisticREG__tol': [1e-4, 1e-3]
    }
]

# for name, model in logistic_reg_pipelines:
#     grid = GridSearchCV(estimator=model, param_grid=param_grid, scoring=SCORING, cv=kfold, n_jobs=4)
#     grid.fit(X_train, y_train)
#     msg = "Sem tratamento de missings: %s - Melhor: %f usando %s" % (name, grid.best_score_, grid.best_params_)
#     print(msg)

# ==============================
# 8. MODEL PREPARATION
# ==============================

print("\nPreparing model...")

# Preparando o modelo
logistic_regression = ('LogisticREG', LogisticRegression(max_iter=1000))
model = Pipeline([tfidf, logistic_regression])
model.fit(X_train, y_train)

# Estimativa da acurácia no conjunto de teste
predictions = model.predict(X_test)
print(f"\nAccuracy: {accuracy_score(y_test, predictions):.3f}")

# Relatório de métricas
print("\nClassification report:")
print(classification_report(y_test, predictions, digits=3))

# Matriz de confusão
print("\nConfusion matrix:")
print(confusion_matrix(y_test, predictions))

# ==============================
# 9. MODEL FINALIZATION
# ==============================

print("\nFinalizing model...")
model = Pipeline([tfidf, logistic_regression])
model.fit(X, y)
print("Model finalized!")

# ==============================
# 10. MODEL DUMP
# ==============================

print("\nDumping model pipeline...")
# model_name = input('\x1b[93m' + "Please enter model file name: " + '\033[0m')
# dump(model, open(f"../pipelines/{model_name}.pkl", 'wb'))
print("Model pipeline dumped!")

# ==============================
# 11. TESTING NEW DATA
# ==============================

print("\nTesting new data...")

# Carrega csv com dados inteiramente novos
df = pd.read_csv('https://raw.githubusercontent.com/carlosedcec/fake-news-predictor/refs/heads/master/api/ml/data/testdata/test_data.csv', sep=';', encoding='utf-8-sig')

# Configura o csv
df["combined_text"] = df["title"].fillna("") + " " + df["text"].fillna("")

# Pré-processa os textos fazendo houldout dos dados
X_entrada = df.progress_apply(preprocess_text, axis=1)

# Faz a predição dos dados
saidas = model.predict(X_entrada)
print(saidas)

# Seta os valores de Y com as saídas esperadas
Y_saidas_esperadas = np.array(df["label"].values, dtype=int)

# Calcula a taxa de acerto
counter = 0
for idx, label in enumerate(Y_saidas_esperadas):
    if label == saidas[idx]:
        counter = counter + 1
result_rate = (counter*100) / len(df["label"].values)

print(f"Test results: {result_rate:.2f}% of correct answers")