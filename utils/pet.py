ORDERED_PET_CLUSTER_FEATURES = [
    'sex',
    'age',
    'pet_size',
    'vaccinated',
    'dewormed',
    'sterilized',
    'has_disabilities',
    'sociability',
    'fur_length',
    'shedding_level',
    'energy_level',
    'care_level_cost',
    'care_difficulty'
]

PET_BOOL_FEATURES = [
    "sex",
    "vaccinated",
    "dewormed",
    "sterilized",
    "has_disabilities",
]

ORDERED_PET_ORDINAL_FEATURES = [
    'pet_size',
    'sociability',
    'fur_length',
    'shedding_level',
    'energy_level',
    'care_level_cost',
    'care_difficulty'
]

PET_ORDINAL_FEATURES_VALUES = {
    'pet_size': [1, 2, 3, 4],
    'sociability': [0, 1, 2, 3],
    'fur_length': [0, 1, 2, 3],
    'shedding_level': [0, 1, 2, 3],
    'energy_level': [1, 2, 3],
    'care_level_cost': [1, 2, 3],
    'care_difficulty': [1, 2, 3],
}

def can_clusterize(pet_data: dict) -> bool:
    """
    Verifica si todos los campos necesarios para clusterizar no son None.
    pet_data puede ser un dict o un modelo Pydantic con .dict().

    Args:
        pet_data (dict): Diccionario con los datos de la mascota.

    Returns:
        bool: True si todos los campos necesarios están presentes, False en caso contrario.
    """
    return all(pet_data.get(field, None) is not None for field in ORDERED_PET_CLUSTER_FEATURES)

def preprocess_pet_data_for_clustering(pet_data: dict) -> list:
    """
    Prepara los datos de la mascota para el clustering.
    Devuelve una lista con los valores en el orden definido por ORDERED_PET_CLUSTER_FEATURES.
    Asume que can_clusterize(pet_data) es True.

    Args:
        pet_data (dict): Diccionario con los datos de la mascota.

    Returns:
        list: Lista de valores preparados para clustering.
    """

    import joblib
    import os
    import pandas as pd

    scaler_path = os.path.join(os.path.dirname(__file__), "../artifacts/Scalers/")
    scaler_path += "age_scaler_dogs.pkl" if pet_data['species'] else "age_scaler_cats.pkl"
    age_scaler = joblib.load(scaler_path)

    feature_values = []

    for field in ORDERED_PET_CLUSTER_FEATURES:
        feature_values.append(pet_data[field])

    df = pd.DataFrame([feature_values], columns=ORDERED_PET_CLUSTER_FEATURES)

    df['age'] = age_scaler.transform(df[['age']])

    df[PET_BOOL_FEATURES] = df[PET_BOOL_FEATURES].astype(int)

    for feature in ORDERED_PET_ORDINAL_FEATURES:
        df[feature] = pd.Categorical(df[feature], categories=PET_ORDINAL_FEATURES_VALUES[feature])
    
    df = pd.get_dummies(df, columns=ORDERED_PET_ORDINAL_FEATURES, dtype=int)

    return df.values.flatten().tolist()