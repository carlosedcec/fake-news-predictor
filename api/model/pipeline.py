import pickle

class Pipeline:
    
    def __init__(self):
        """Initializes the pipeline"""
        self.pipeline = None
    
    def carrega_pipeline(self, path):
        """Loads the pipeline built during the training phase"""
        with open(path, 'rb') as file:
             self.pipeline = pickle.load(file)
        return self.pipeline