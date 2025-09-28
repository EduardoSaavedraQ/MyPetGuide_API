import joblib
import os

SCALERS_PATH = os.path.join(os.path.dirname(__file__), "../../ml_models/Scalers/")

def load_scaler(scaler_type: str):
    if scaler_type not in {"owner", "pet"}:
        raise ValueError("Invalid scaler type. Choose 'owner' or 'pet'.")
    
    return joblib.load(os.path.join(SCALERS_PATH, f"{scaler_type}_scaler.pkl"))

def scale_data(scaler_type: str, data: list):
    # Si data es una lista plana, la convertimos a lista de listas
    if isinstance(data, list) and all(isinstance(x, (int, float)) for x in data):
        data_to_scale = [data]
    # Si data es una lista de listas, la usamos tal cual
    elif isinstance(data, list) and all(isinstance(row, list) and all(isinstance(x, (int, float)) for x in row) for row in data):
        data_to_scale = data
    else:
        raise ValueError("Data must be a list of numbers or a list of lists of numbers.")

    scaler = load_scaler(scaler_type)
    return scaler.transform(data_to_scale)