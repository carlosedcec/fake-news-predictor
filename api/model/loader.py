import pandas as pd
import numpy as np

class Loader:

    def __init__(self):
        """Initializes de loader"""
        pass

    def load_data(self, url: str):
        """Loads and returns a DataFrame"""
        df = pd.read_csv(url, sep=None, engine="python", encoding="utf-8")
        return self.__sanitize_data(df)

    def __sanitize_data(self, df):
        """Cleans and sanitizes the dataframe data"""

        # Normalizes dataframe columns
        df.columns = df.columns.str.strip().str.lower()
        for col in ["title", "text", "label"]:
            if col not in df.columns:
                df[col] = np.nan if col != "text" else ""

        # Title and label configuration
        df["combined_text"] = df["title"].fillna("") + " " + df["text"].fillna("")
        df["label"] = (df["label"].astype(str).map({ "real": 1, "fake": 0, "1": 1, "0": 0 }))

        # Finalizes the dataframe and drop null columns
        df = df[["combined_text", "label"]]
        df = df.dropna(subset=["combined_text", "label"])

        return df