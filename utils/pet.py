ORDERED_PET_CLUSTER_FEATURES: list = [
    "sex",
    "age",
    "pet_size",
    "vaccinated",
    "dewormed",
    "sterilized",
    "has_disabilities",
    "sociability",
    "fur_length",
    "shedding_level",
    "energy_level",
    "care_level_cost",
    "care_difficulty"
]

PET_BOOL_FEATURES: list = [
    "sex",
    "vaccinated",
    "dewormed",
    "sterilized",
    "has_disabilities",
]

ORDERED_PET_ORDINAL_FEATURES: list = [
    "pet_size",
    "sociability",
    "fur_length",
    "shedding_level",
    "energy_level",
    "care_level_cost",
    "care_difficulty"
]

PET_ORDINAL_FEATURES_VALUES: dict = {
    "pet_size": [1, 2, 3, 4],
    "sociability": [0, 1, 2, 3],
    "fur_length": [0, 1, 2, 3],
    "shedding_level": [0, 1, 2, 3],
    "energy_level": [1, 2, 3],
    "care_level_cost": [1, 2, 3],
    "care_difficulty": [1, 2, 3],
}

DOG_CLUSTER_0_SUMMARY: str = """
    Los siguientes son los perros con el perfil más "estándar". Predominan los machos adultos jóvenes (promedio de 3.3 años), de
    tamaño mediano a grande. Tienen un perfil perfectamente balaneado con niveles normales de energía y sociabilidad y, además,
    son relativamente fáciles de cuidar. Encontrarás que la mayoría de estos perros están perfectamente sanos, siendo que ya cuentan
    con sus vacunas, están desparasitados y esterilizados.

    Estos perros son ideales para dueños que buscan un perro predecible, ya maduro, sin sorpresas.
"""

DOG_CLUSTER_1_SUMMARY: str = """
    Estos perros son de bajo mantenimiento. En su mayoría son adultos jóvenes (promedio de 3.4 años) de tamaño chico. Son
    universalmente amigables con una gran tendencia a ser muy sociables tanto con humanos como con otras mascotas. La mayoría de
    estos poseen un pelaje corto que no requiere mucho cuidado y son muy fáciles de cuidar y mantener en general. Poseen un nivel
    normal de energía.

    Estos perros son ideales para dueños primerizos, personas con presupuestos ajustados o que viven en espacios más pequeños.
"""

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
    scaler_path += "age_scaler_dogs.pkl" if pet_data["species"] else "age_scaler_cats.pkl"
    age_scaler = joblib.load(scaler_path)

    feature_values = []

    for field in ORDERED_PET_CLUSTER_FEATURES:
        feature_values.append(pet_data[field])

    df = pd.DataFrame([feature_values], columns=ORDERED_PET_CLUSTER_FEATURES)

    df["age"] = age_scaler.transform(df[["age"]])

    df[PET_BOOL_FEATURES] = df[PET_BOOL_FEATURES].astype(int)

    for feature in ORDERED_PET_ORDINAL_FEATURES:
        df[feature] = pd.Categorical(df[feature], categories=PET_ORDINAL_FEATURES_VALUES[feature])
    
    df = pd.get_dummies(df, columns=ORDERED_PET_ORDINAL_FEATURES, dtype=int)

    return df.values.flatten().tolist()