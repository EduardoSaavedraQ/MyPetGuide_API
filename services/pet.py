from supabase import Client
from typing import Any
from services.image_services import upload_image_to_supabase
from services.ml.kmeans_service import predict_cluster
from services.ml.scaler_service import scale_data
from services.ml.decission_tree_service import predict_compatible_cluster
from utils.pet import preprocess_pet_data_for_clustering, can_clusterize as can_clusterize_pet
from utils.user import can_clusterize as can_clusterize_user, ORDERED_USER_CLUSTER_FEATURES, USER_BOOL_FEATURES, USER_FEAUTURES_TO_SCALE, transform_bool_cluster_features_to_int as transform_bool_user
from fastapi import HTTPException, status
from numpy import ndarray
from postgrest.base_request_builder import APIResponse
from storage3.exceptions import StorageApiError

def create_pet(
        data: dict[str, Any],
        image: bytes | None,
        id_user: str,
        supabase: Client
) -> dict[str, Any]:
    """Orquesta la creación completa de un perfil de mascota.

    Esta función de servicio maneja toda la lógica de negocio para registrar una
    nueva mascota en el sistema. El proceso incluye:
    1.  Subir una imagen de perfil a Supabase Storage (si se proporciona).
    2.  Asignar la mascota al usuario propietario (`id_owner`).
    3.  Si hay suficientes datos, procesar las características de la mascota,
        escalarlas y asignarle un clúster (`pet_label`) mediante un modelo K-means.
    4.  Insertar el registro final en la tabla `pets` de la base de datos.
    5.  Consultar y devolver el perfil completo de la mascota recién creada,
        incluyendo los datos anidados de sus razas.

    Args:
        data (dict[str, Any]): Diccionario con los datos ya validados del perfil
                            de la mascota (usualmente desde un modelo `PetCreate`).
        image (bytes | None): La imagen de perfil en formato de bytes, o `None` si
                            no se proporcionó ninguna.
        id_user (str): El UUID del usuario autenticado que se registrará como
                    el dueño de la mascota.
        supabase (Client): Una instancia activa del cliente de Supabase.

    Returns:
        dict[str, Any]: Un diccionario que representa el perfil completo de la
                        mascota recién creada, con los datos de las razas
                        anidados, listo para ser enviado como respuesta de la API.
    """

    if image is not None:

        upload_response = upload_image_to_supabase(
            id=id_user, image=image, bucket="avatars", path="public/pets", supabase=supabase
        )

        data["photo_url"] = upload_response.path

    data["id_owner"] = id_user

    if can_clusterize_pet(data) and data.get("species") is not None:
        preprocessed_pet_data: list = preprocess_pet_data_for_clustering(data)
        cluster = predict_cluster("cat" if not data["species"] else "dog", preprocessed_pet_data)
        data["pet_label"] = cluster[0]

    data.pop("species")

    response = (
        supabase.table("pets")
        .insert(data)
        .execute()
    )

    created_pet: dict[str, Any] = response.data[0]

    response = (
        supabase.table("pets")
        .select("*, main_breed:id_breed1!inner(*), secondary_breed:id_breed2(*)'")
        .eq("id_pet", created_pet["id_pet"])
        .execute()
    )

    created_pet = response.data[0]

    return created_pet

def get_all_pets_in_adoption(supabase: Client, id_user: str, page: int | None = None) -> list[dict[str, Any]]:
    """Obtiene una lista paginada de todas las mascotas en adopción.

    Esta función consulta la base de datos para recuperar todas las mascotas que
    están marcadas con `in_adoption_process = True`. Excluye las mascotas que
    pertenecen al usuario que realiza la solicitud para evitar que vea sus
    propias mascotas en el listado. Además, genera URLs firmadas y temporales
    para las imágenes de las mascotas.

    Args:
        supabase (Client): Instancia del cliente de Supabase.
        id_user (str): El UUID del usuario que realiza la consulta.
        page (int | None): Opcional, el número de página para la paginación.

    Raises:
        ValueError: Si el número de página es menor o igual a 0.

    Returns:
        list[dict[str, Any]]: Una lista de diccionarios, donde cada uno representa
                            el perfil de una mascota en adopción.
    """

    if page <= 0:
        raise ValueError("El número de página debe ser mayor a 0.")

    query = (
        supabase.table("pets")
        .select("*, species:id_breed1(species), main_breed:id_breed1!inner(*), secondary_breed:id_breed2(*)")
        .eq("in_adoption_process", True)
        .neq("id_owner", id_user)
    )

    if page is not None:
        limit = 15
        offset = (page - 1) * limit

        query = query.range(offset, offset + limit - 1)
    
    response = query.execute()

    for pet in response.data:
        if pet["photo_url"] is not None:
            pet["photo_url"] = supabase.storage.from_("avatars").create_signed_url(path=pet["photo_url"], expires_in=60)

    return response.data

def get_recommended_pets(supabase: Client, id_user: str, page: int | None = None) -> list[dict[str, Any]]:
    """Obtiene una lista de mascotas recomendadas para un usuario específico.

    Esta es la función principal del sistema de recomendación. Sigue un proceso
    de varios pasos:
    1.  Obtiene y valida el perfil del usuario.
    2.  Preprocesa las características del usuario (escalado, transformación).
    3.  Utiliza un modelo de árbol de decisión para predecir el clúster de mascotas
        (`pet_label`) que es más compatible con el perfil del usuario.
    4.  Busca en la base de datos todas las mascotas en adopción que pertenezcan
        a ese clúster y coincidan con la especie preferida del usuario.
    5.  Genera URLs firmadas para las imágenes de las mascotas recomendadas.

    Args:
        supabase (Client): Instancia del cliente de Supabase.
        id_user (str): El UUID del usuario para quien se generarán las recomendaciones.
        page (int | None): Opcional, el número de página para la paginación.

    Raises:
        HTTPException (404): Si no se encuentra el perfil del usuario.
        HTTPException (400): Si el perfil del usuario no tiene suficientes datos
                            para generar una recomendación, o si el número de
                            página es inválido.

    Returns:
        list[dict[str, Any]]: Una lista con los perfiles de las mascotas compatibles.
    """

    user_profile_response = (
        supabase.table("users_profiles")
        .select(", ".join(ORDERED_USER_CLUSTER_FEATURES + ["preferred_species"]))
        .eq("id_user", id_user)
        .execute()
    )

    if not user_profile_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró el perfil del usuario."
        )

    user_data: dict = user_profile_response.data[0]

    if not can_clusterize_user(user_data):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tu perfil de usuario no tiene suficientes datos para recomendar mascotas."
        )
    
    user_data = transform_bool_user(user_data)
    bool_features = [user_data[field] for field in USER_BOOL_FEATURES]
    features_to_scale = [user_data[field] for field in USER_FEAUTURES_TO_SCALE]
    scaled_data = scale_data("owner", features_to_scale)
    features = scaled_data[0] + bool_features

    pet_label = predict_compatible_cluster(
        "user_to_dogs" if user_data["preferred_species"] else "user_to_cats",
        features
    )[0]

    query = (
        supabase.table("pets")
        .select("*, species:id_breed1(species), main_breed:id_breed1!inner(*), secondary_breed:id_breed2(*)")
        .eq("in_adoption_process", True)
        .neq("id_owner", id_user)
        .eq("pet_label", pet_label)
        #.eq("species.species", user_data["preferred_species"])
    )

    if page is not None:
        if page <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El número de página debe ser mayor a 0."
            )
        
        limit = 15
        offset = (page - 1) * limit

        query = query.range(offset, offset + limit - 1)

    response = query.execute()

    results = list(filter(lambda pet: pet["species"]["species"] == user_data["preferred_species"], response.data))

    for pet in response.data:
        if pet["photo_url"] is not None:
            pet["photo_url"] = supabase.storage.from_("avatars").create_signed_url(path=pet["photo_url"], expires_in=3600)

    return results

def get_compatible_pet_clusters(user_features: dict[str, int | bool]) -> dict[str, list[int | float | str]]:
    """
    Devuelve un diccionario que contiene listas ordenadas con las clases del KNN correspondiente a la especie preferida,
    sus porcentajes de probabilidad y sus respectivas descripciones. El orden es descendente según el porcentaje de probabilidad.

    Args:
        user_features (dict[str, list[int|float|str]]): Diccionario con las características del usuario.

    Raises:
        HTTPException (400): Si faltan campos o valores en las características del usuario necesarios para el modelo de KNN.

    Returns:
        dict[str, list[int | float | str]]: Diccionario con los campos `pet_clusters`, `probabilities` y `clusters_descriptions`.
    """

    from utils.user import can_predict, preprocess_user_data_for_prediction
    from utils.pet import load_pet_clusters_descriptions, load_pet_clusters_titles
    from services.ml.knn_service import predict_compatible_clusters, get_knn_classes, sort_clusters_by_probability

    if not can_predict(user_features):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tu perfil de usuario no tiene suficientes datos para recomendar mascotas."
        )    

    preprocessed_data: list = preprocess_user_data_for_prediction(user_features)

    preferred_species: bool = user_features["preferred_species"]

    knn_type: str = "user_to_dogs" if preferred_species else "user_to_cats"

    pet_classes: list = get_knn_classes(knn_type)

    probabilities: ndarray = predict_compatible_clusters(knn_type, preprocessed_data)

    sorted_probabilities, sorted_classes = sort_clusters_by_probability(probabilities=probabilities.tolist()[0], clusters=pet_classes)

    while sorted_probabilities[-1] == 0:
        sorted_probabilities.pop()
        sorted_classes.pop()

    clusters_descriptions: list[str] = load_pet_clusters_descriptions(preferred_species, sorted_classes)
    clusters_titles: list[str] = load_pet_clusters_titles(preferred_species, sorted_classes)

    compatible_pet_clusters: dict[str, list[int | float | str]] = {
        "pet_clusters": sorted_classes,
        "probabilities": sorted_probabilities,
        "clusters_descriptions" : clusters_descriptions,
        "clusters_titles": clusters_titles
    }

    return compatible_pet_clusters

def get_pets_by_pet_cluster(supabase: Client, id_user: str, cluster: int, page: int | None = None) -> list[dict[str, Any]]:
    """
    Devuelve una lista con las mascotas del clúster especificado, según la especie preferida del usuario.

    Args:
        supabase (Client): Cliente de Supabase mediante el cual se realizarán las consultas a la base de datos alojada en
                            el servidor de supabase.
        id_user (str): El UUID del usuario para el cual se devuelven las mascotas. Se utiliza para obtener la especie
                        preferida y para evitar que se le devuelvan sus propias mascotas (si las hay).
        cluster (int): El número de clúster perteneciente a las mascotas que se quieren obtener.
        page (int | None): El número de página para la paginación de los resultados.

    Raises:
        HTTPException (404): Si no se encuentra el perfil del usuario.
        HTTPException (400): Si el perfil del usuario no tiene suficientes datos
                            para generar una recomendación, o si el número de
                            página es inválido.

    Returns:
        list[dict[str, Any]]: Una lista con los perfiles de las mascotas compatibles.
    """

    user_query_response: APIResponse = (
        supabase.table("users_profiles")
        .select("preferred_species")
        .eq("id_user", id_user)
        .execute()
    )

    if not user_query_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario especificado no cuanta con un perfil"
        )

    preferred_species: bool = user_query_response.data[0]["preferred_species"]

    pets_query = (
        supabase.table("pets")
        .select("*, species:id_breed1(species), main_breed:id_breed1!inner(*), secondary_breed:id_breed2(*)")
        .eq("in_adoption_process", True)
        .neq("id_owner", id_user)
        .eq("pet_label", cluster)
        .eq("main_breed.species", preferred_species)
    )

    if page is not None:
        if page <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El número de página debe ser mayor a 0."
            )
        
        limit = 15
        offset = (page - 1) * limit

        pets_query = pets_query.range(offset, offset + limit - 1)

    pets_query_response: APIResponse = pets_query.execute()

    pets: list[dict[str, Any]] = pets_query_response.data

    for pet in pets:
        if pet["photo_url"]:
            try:
                pet["photo_url"] = supabase.storage.from_("avatars").create_signed_url(
                    path=pet["photo_url"],
                    expires_in=3600
                )["signedURL"]

            except StorageApiError:
                pet["photo_url"] = None

    return pets