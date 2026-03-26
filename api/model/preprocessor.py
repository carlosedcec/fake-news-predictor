import re
import pickle
import numpy as np

from sklearn.model_selection import train_test_split

import nltk
from nltk.corpus import stopwords

nltk.download("punkt")
nltk.download("stopwords")
nltk.download("wordnet")
nltk.download("omw-1.4")


class PreProcessor:

    def __init__(self):
        """Inicializa o preprocessador"""
        pass

    def separa_teste_treino(self, dataset, percentual_teste, seed=7):
        """ Cuida de todo o pré-processamento. """
        # limpeza dos dados e eliminação de outliers

        # feature selection

        # divisão em treino e teste
        X_train, X_test, Y_train, Y_test = self.__preparar_holdout(dataset,
                                                                  percentual_teste,
                                                                  seed)
        # normalização/padronização
        
        return (X_train, X_test, Y_train, Y_test)
    
    def __preparar_holdout(self, dataset, percentual_teste, seed):
        """ Divide os dados em treino e teste usando o método holdout.
        Assume que a variável target está na última coluna.
        O parâmetro test_size é o percentual de dados de teste.
        """
        dados = dataset.values
        X = dados[:, 0:-1]
        Y = dados[:, -1]
        return train_test_split(X, Y, test_size=percentual_teste, random_state=seed)
    
    def preprocess_text(self, form):
        """
        Função completa para limpar e pré-processar um único documento de texto.
        Aplica todos os passos da proposta: remoção de metadados, lowering,
        remoção de pontuação/números, tokenização e remoção de stopwords.
        """

        def sanitize_text(text):
            text = re.sub(r"--.*", "", text, flags=re.DOTALL) # Remove assinaturas (começando com '-- ')
            text = re.sub(r">.*", "", text) # Remove linhas de citação (começando com '>')
            text = re.sub(r"\S*@\S*\s?", "", text) # Remove emails
            text = re.sub(r"\s+", " ", text).strip() # Remove quebras de linha e tabs
            text = text.lower()    
            return text

        text = form.title + form.text
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
    
    def scaler(self, X_train):
        """ Normaliza os dados. """
        # normalização/padronização
        scaler = pickle.load(open('./MachineLearning/scalers/minmax_scaler_diabetes.pkl', 'rb'))
        reescaled_X_train = scaler.transform(X_train)
        return reescaled_X_train
