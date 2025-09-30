import joblib
import os

DECISION_TREE_MODELS_PATH = os.path.join(os.path.dirname(__file__), "../../artifacts/DecisionTrees/")

def load_decision_tree_model(model_type: str):
    if model_type not in ["user_to_dogs", "user_to_cats", "dog_to_user", "cat_to_user"]:
        raise ValueError("Invalid decision tree type. Choose from 'user_to_dogs', 'owner_to_cats', 'dog_to_users', or 'cat_to_users'.")

    return joblib.load(os.path.join(DECISION_TREE_MODELS_PATH, f"{model_type}_decission_tree.pkl"))

def predict_compatible_cluster(model_type: str, data: list) -> list:
    # Si data es una lista plana, la convertimos a lista de listas
    if isinstance(data, list) and all(isinstance(x, (int, float)) for x in data):
        data_to_predict = [data]
    # Si data es una lista de listas, la usamos tal cual
    elif isinstance(data, list) and all(isinstance(row, list) and all(isinstance(x, (int, float)) for x in row) for row in data):
        data_to_predict = data
    else:
        raise ValueError("Decision tree needs data to be a list of numbers or a list of lists of numbers.")

    model = load_decision_tree_model(model_type)
    
    predictions = model.predict(data_to_predict)

    return [int(p) for p in predictions]