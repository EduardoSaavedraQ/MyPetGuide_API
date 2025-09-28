USER_CLUSTER_FEATURES = [
    "house_size",
    "house_backyard_size",
    "family_size",
    "available_time_per_day",
    "experience_with_pets",
    "has_kids",
    "has_neighbors",
    "vet_access",
    "has_other_pets"
]

USER_FEAUTURES_TO_SCALE = [
    "house_size",
    "house_backyard_size",
    "family_size",
    "available_time_per_day",
    "experience_with_pets",
]

USER_BOOL_FEATURES = [
    "has_kids",
    "has_neighbors",
    "vet_access",
    "has_other_pets"
]

def can_clusterize(user_data: dict) -> bool:
    """
    Verifica si todos los campos necesarios para clusterizar no son None.
    user_data puede ser un dict o un modelo Pydantic con .dict().
    """
    return all(user_data.get(field) is not None for field in USER_CLUSTER_FEATURES)

def transform_bool_cluster_features_to_int(data: dict) -> dict:
    """
    Transforma los campos booleanos en enteros (True -> 1, False -> 0).
    Modifica el diccionario original.
    """
    for field in USER_BOOL_FEATURES:
        if field in data and isinstance(data[field], bool):
            data[field] = int(data[field])
    return data