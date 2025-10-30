ORDERED_USER_CLUSTER_FEATURES = [
    "house_size",
    "house_backyard_size",
    "family_size",
    "has_kids",
    "has_neighbors",
    "available_time_per_day",
    "vet_access",
    "has_other_pets",
    "experience_with_pets"
]

ORDERED_USER_FEATURES = [
    "house_size",
    "house_backyard_size",
    "family_size",
    "age",
    "activity_level",
    "has_kids",
    "has_neighbors",
    "available_time_per_day",
    "vet_access",
    "has_other_pets",
    "experience_with_pets"
]

USER_FEAUTURES_TO_SCALE = [
    "house_size",
    "house_backyard_size",
    "family_size",
    "age",
    "available_time_per_day"
]

USER_BOOL_FEATURES = [
    "has_kids",
    "has_neighbors",
    "vet_access",
    "has_other_pets"
]

ORDERED_USER_ORDINAL_FEATURES = [
    "activity_level",
    "experience_with_pets"
]

USER_ORDINAL_FEATURES_VALUES: dict = {
    "activity_level": [1, 2, 3],
    "experience_with_pets": [0, 1, 2, 3],
}

def can_clusterize(user_data: dict) -> bool:
    """
    Verifica si todos los campos necesarios para clusterizar no son None.
    user_data puede ser un dict o un modelo Pydantic con .dict().
    """
    return all(user_data.get(field) is not None for field in ORDERED_USER_CLUSTER_FEATURES)

def transform_bool_cluster_features_to_int(data: dict) -> dict:
    """
    Transforma los campos booleanos en enteros (True -> 1, False -> 0).
    Modifica el diccionario original.
    """
    for field in USER_BOOL_FEATURES:
        if field in data and isinstance(data[field], bool):
            data[field] = int(data[field])
    return data

def can_predict(user_data: dict) -> bool:
    """
    Verifica si todos los campos necesarios para predecir el clúster de mascota compatible no son None.
    
    Args:
        user_data (dict): Diccionario con los datos del usuario.
    """
    return all(user_data.get(field) is not None for field in ORDERED_USER_FEATURES)

def preprocess_user_data_for_prediction(user_data: dict) -> list:
    """
    Prepara los datos del usuario para la predicción.
    Devuelve una lista con los valores en el orden definido por ORDERED_USER_FEATURES.
    Asume que can_predict(user_data) es True.

    Args:
        user_data (dict): Diccionario con los datos del usuario.

    Returns:
        list: Lista de valores preparados para predicción.

    """

    import joblib
    import os
    import pandas as pd

    scaler_path = os.path.join(os.path.dirname(__file__), "../artifacts/Scalers/owner_scaler.pkl")
    user_data_scaler = joblib.load(scaler_path)

    feature_values = []

    for field in ORDERED_USER_FEATURES:
        feature_values.append(user_data[field])

    df = pd.DataFrame([feature_values], columns=ORDERED_USER_FEATURES)

    scaled_quantitative_features = user_data_scaler.transform(df[USER_FEAUTURES_TO_SCALE].to_numpy())

    df_quantitative_features = pd.DataFrame(scaled_quantitative_features, columns=USER_FEAUTURES_TO_SCALE)

    df_bool_features = df[USER_BOOL_FEATURES].copy()

    df_bool_features = df_bool_features.astype(int)

    for feature in ORDERED_USER_ORDINAL_FEATURES:
        df[feature] = pd.Categorical(df[feature], categories=USER_ORDINAL_FEATURES_VALUES[feature])

    df_ordinal_features = df[ORDERED_USER_ORDINAL_FEATURES].copy()

    df_ordinal_features = pd.get_dummies(df_ordinal_features, columns=ORDERED_USER_ORDINAL_FEATURES, dtype=int)

    df_processed = pd.concat(
        [df_quantitative_features, df_ordinal_features, df_bool_features], 
        axis=1
    )

    return df_processed.values.flatten().tolist()