import joblib
import os
from numpy import ndarray

KNN_MODELS_PATH = os.path.join(os.path.dirname(__file__), "../../artifacts/KNN/")

def load_knn_model(model_type: str):
    """
    Carga el modelo KNN serializado a partir del `model_type` indicado.

    Args:
        model_type (str): String que indica el modelo de KNN que se quiere utilizar.

    Returns:
        Modelo de KNN.
    """

    if model_type not in ["user_to_dogs", "user_to_cats"]:
        raise ValueError("Invalid KNN type. Choose from 'user_to_dogs' or 'user_to_cats'.")

    return joblib.load(os.path.join(KNN_MODELS_PATH, f"knn_{model_type}.pkl"))

def get_knn_classes(model_type: str) -> list:
    """
    Devuelve una lista con las clases utilizadas en la construcción del modelo de KNN
    especificado por `model_type`

    Args:
        model_type (str): String que indica el modelo de KNN que se quiere utilizar.

    Returns:
        list: Una lista ordenada con las clases del KNN.
    """

    model = load_knn_model(model_type)

    return model.classes_.tolist()

def predict_compatible_clusters(model_type: str, data: list) -> ndarray:
    """
    Devuelve un array con los porcentajes de probabilidad con cada una de las clases utilizadas
    en el modelo de KNN especificado por `model_type`.

    Args:
        model_type (str): String que indica el modelo de KNN que se quiere utilizar.
        data (list): Lista ordenada que contiene los datos necesarios para realizar la predicción.

    Returns:
        ndarray: Array de NumPy con las probabilidades respectivas de las clases.
    """

    # Si data es una lista plana, la convertimos a lista de listas
    if isinstance(data, list) and all(isinstance(x, (int, float)) for x in data):
        data_to_predict: list[list] = [data]
    # Si data es una lista de listas, la usamos tal cual
    elif isinstance(data, list) and all(isinstance(row, list) and all(isinstance(x, (int, float)) for x in row) for row in data):
        data_to_predict: list[list] = data
    else:
        raise ValueError("KNN needs data to be a list of numbers or a list of lists of numbers.")

    model = load_knn_model(model_type)

    predictions: ndarray = model.predict_proba(data_to_predict)

    return predictions

def sort_clusters_by_probability(probabilities: list[float], clusters: list[int]) -> tuple[list[float], list[int]]:
    """
    Ordena las probabilidades de mayor a menor y mantiene sincronizadas las clases.
    En caso de empate en probabilidades, mantiene el orden original de las clases.

    Args:
        probabilities (list[float]): Lista de probabilidades [0.3, 0.5, 0.2]
        clusters (list[int]): Lista de clases/clusters [0, 1, 2]
        
    Returns:
        tuple: (probabilidades_ordenadas, clusters_ordenados)

    Example:
        # Con empate:
        probs = [0.4, 0.4, 0.2]
        clusters = [0, 1, 2]
        # Returns: ([0.4, 0.4, 0.2], [0, 1, 2])  # Mantiene orden original en empate
    """

    if len(probabilities) != len(clusters):
        raise ValueError("Las listas de probabilidades y clusters deben tener la misma longitud")
        
    # Enumerar para mantener el orden original en caso de empate
    indexed_pairs = list(enumerate(zip(probabilities, clusters)))
    
    # Ordenar por probabilidad (mayor a menor) y por índice original (para empates)
    # El índice original asegura que en caso de empate se mantenga el orden inicial
    indexed_pairs.sort(key=lambda x: (-x[1][0], x[0]))
    
    # Desempaquetar los pares ordenados, ignorando los índices
    sorted_probs = [p for _, (p, _) in indexed_pairs]
    sorted_clusters = [c for _, (_, c) in indexed_pairs]
    
    return sorted_probs, sorted_clusters