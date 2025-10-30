import joblib
import os

KNN_MODELS_PATH = os.path.join(os.path.dirname(__file__), "../../artifacts/KNN/")

def load_knn_model(model_type: str):
    if model_type not in ["user_to_dogs", "user_to_cats"]:
        raise ValueError("Invalid KNN type. Choose from 'user_to_dogs' or 'user_to_cats'.")

    return joblib.load(os.path.join(KNN_MODELS_PATH, f"knn_{model_type}.pkl"))

def get_knn_classes(model_type: str) -> list:
    model = load_knn_model(model_type)

    return model.classes_.tolist()

def predict_compatible_clusters(model_type: str, data: list):
    # Si data es una lista plana, la convertimos a lista de listas
    if isinstance(data, list) and all(isinstance(x, (int, float)) for x in data):
        data_to_predict = [data]
    # Si data es una lista de listas, la usamos tal cual
    elif isinstance(data, list) and all(isinstance(row, list) and all(isinstance(x, (int, float)) for x in row) for row in data):
        data_to_predict = data
    else:
        raise ValueError("KNN needs data to be a list of numbers or a list of lists of numbers.")

    model = load_knn_model(model_type)

    predictions = model.predict_proba(data_to_predict)

    return predictions