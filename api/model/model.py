import pickle

class Model:
    
    def __init__(self):
        """Initializes the model"""
        self.model = None
    
    def load_model(self, path):
        if path.endswith('.pkl'):
            with open(path, 'rb') as file:
                self.model = pickle.load(file)
        else:
            raise Exception('File format not supported')
        return self.model
    
    def preditor(self, X_input):
        """Performs a news prediction based on the trained model"""
        if self.model is None:
            raise Exception('The model was not loaded. Use load_model() first')
        label = self.model.predict(X_input)
        return label