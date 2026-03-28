from sklearn.metrics import accuracy_score

class Evaluator:
    
    def __init__(self):
        """Inicializa o avaliador"""
        pass

    def evaluate(self, model, X_test, Y_test):
        """ Faz uma predição e avalia o modelo. Poderia parametrizar o tipo de
        avaliação, entre outros.
        """
        predictions = model.predict(X_test)
        # Caso o seu problema tenha mais do que duas classes, altere o parâmetro average
        return accuracy_score(Y_test, predictions)
                
