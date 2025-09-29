PET_CLUSTER_FEATURES = [
    "age",
    "pet_size",
    "sociability",
    "fur_length",
    "shedding_level",
    "energy_level",
    "care_level_cost",
    "care_dificulty",
    "sex",
    "vaccinated",
    "dewormed",
    "sterilized",
    "has_disabilities",
]

PET_FEATURES_TO_SCALE = [
    "age",
    "pet_size",
    "sociability",
    "fur_length",
    "shedding_level",
    "energy_level",
    "care_level_cost",
    "care_dificulty",
]

PET_BOOL_FEATURES = [
    "sex",
    "vaccinated",
    "dewormed",
    "sterilized",
    "has_disabilities",
]

def can_clusterize(pet_data: dict) -> bool:
    """
    Verifica si todos los campos necesarios para clusterizar no son None.
    pet_data puede ser un dict o un modelo Pydantic con .dict().
    """
    return all(pet_data.get(field) is not None for field in PET_CLUSTER_FEATURES)

def transform_bool_cluster_features_to_int(data: dict) -> dict:
    """
    Transforma los campos booleanos en enteros (True -> 1, False -> 0).
    Modifica el diccionario original.
    """
    for field in PET_BOOL_FEATURES:
        if field in data and isinstance(data[field], bool):
            data[field] = int(data[field])
    return data