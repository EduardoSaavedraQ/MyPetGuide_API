import joblib
import os

SCALERS_PATH = os.path.join(os.path.dirname(__file__), "../../artifacts/Scalers/")

def load_scaler(scaler_type: str):
    """Carga el escalador especificado en `scaler_type`.
    Valores válidos: 'owner' y 'pet'.
    """
    if scaler_type not in {"owner", "pet"}:
        raise ValueError("Invalid scaler type. Choose 'owner' or 'pet'.")
    
    return joblib.load(os.path.join(SCALERS_PATH, f"{scaler_type}_scaler.pkl"))

def scale_data(scaler_type: str, data: list) -> list:
    """Escala los valores recibidos en `data` según el tipo especificado.

    Args:
        scaler_type (str): Tipo de escalador que se desea usar.
        data (list): Una lista que contiene los valores de un registro o varios registros con valores que se desean escalar.

    Returns:
        list: Valores escalados.
    """

    # Si data es una lista plana, la convertimos a lista de listas
    if isinstance(data, list) and all(isinstance(x, (int, float)) for x in data):
        data_to_scale = [data]
    # Si data es una lista de listas, la usamos tal cual
    elif isinstance(data, list) and all(isinstance(row, list) and all(isinstance(x, (int, float)) for x in row) for row in data):
        data_to_scale = data
    else:
        raise ValueError("Scaler needs data to be a list of numbers or a list of lists of numbers.")

    scaler = load_scaler(scaler_type)
    return scaler.transform(data_to_scale).tolist()