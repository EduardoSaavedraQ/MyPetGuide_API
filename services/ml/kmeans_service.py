from .scaler_service import scale_data
import joblib
import os

KMEANS_MODELS_PATH = os.path.join(os.path.dirname(__file__), "../../artifacts/KMeans/")

def load_kmeans_model(kmeans_type: str):
    if kmeans_type not in ["cat", "dog", "owner"]:
        raise ValueError("Invalid kmeans type. Choose from 'cat', 'dog', or 'owner'.")
    
    return joblib.load(os.path.join(KMEANS_MODELS_PATH, f"{kmeans_type}_kmeans.pkl"))

def predict_cluster(kmeans_type: str, data: list) -> list:
    # Si data es una lista plana, la convertimos a lista de listas
    if isinstance(data, list) and all(isinstance(x, (int, float)) for x in data):
        data_to_predict = [data]
    # Si data es una lista de listas, la usamos tal cual
    elif isinstance(data, list) and all(isinstance(row, list) and all(isinstance(x, (int, float)) for x in row) for row in data):
        data_to_predict = data
    else:
        raise ValueError("Kmeans needs data to be a list of numbers or a list of lists of numbers.")

    model = load_kmeans_model(kmeans_type)
    
    clusters = model.predict(data_to_predict)

    return [int(c) for c in clusters]