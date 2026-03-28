import pandas as pd
import numpy as np

class Loader:

    def __init__(self):
        """Inicializa o carregador"""
        pass

    def load_data(self, url: str):
        """ Carrega e retorna um DataFrame. Há diversos parâmetros 
        no read_csv que poderiam ser utilizados para dar opções 
        adicionais.
        """
        df = pd.read_csv(url, sep=None, engine="python", encoding="utf-8")
        return self.__sanitize_data(df)

    def __sanitize_data(self, df):
        """ Carrega e retorna um DataFrame. Há diversos parâmetros 
        no read_csv que poderiam ser utilizados para dar opções 
        adicionais.
        """

        # Normaliza as colunas do dataframe
        df.columns = df.columns.str.strip().str.lower()
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