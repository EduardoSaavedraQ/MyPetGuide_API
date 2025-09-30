from supabase import Client
from typing import Any
from services.image_service import replace_image_profile, upload_image_to_supabase
from services.ml.kmeans_service import predict_cluster
from services.ml.scaler_service import scale_data
from services.ml.decission_tree_service import predict_compatible_cluster
from utils.pet import PET_FEATURES_TO_SCALE, PET_BOOL_FEATURES, can_clusterize as can_clusterize_pet, transform_bool_cluster_features_to_int as transform_bool_pet
from utils.user import can_clusterize as can_clusterize_user, USER_CLUSTER_FEATURES, USER_BOOL_FEATURES, USER_FEAUTURES_TO_SCALE, transform_bool_cluster_features_to_int as transform_bool_user
from fastapi import HTTPException, status

def create_pet(
        data: dict[str, Any],
        image: bytes | None,
        id_user: str,
        supabase: Client
) -> dict[str, Any]:
    if image is not None:
        # Si ya hay foto, reemplazar; si no, subir nueva
        if data.get("photo_url"):
            upload_response = replace_image_profile(
                id=id_user, image=image, bucket="avatars", path="public/pets", supabase=supabase
            )
        else:
            upload_response = upload_image_to_supabase(
                id=id_user, image=image, bucket="avatars", path="public/pets", supabase=supabase
            )
        data["photo_url"] = upload_response.path
        
    data["id_owner"] = id_user

    if can_clusterize_pet(data) and data.get("species") is not None:
        data = transform_bool_pet(data)
        bool_features = [data[field] for field in PET_BOOL_FEATURES]
        features_to_scale = [data[field] for field in PET_FEATURES_TO_SCALE]
        scaled_data = scale_data("pet", features_to_scale)
        features = scaled_data[0] + bool_features
        cluster = predict_cluster("cat" if not data["species"] else "dog", features)
        data["pet_label"] = cluster[0]

    data.pop("species")

    response = (
        supabase.table("pets")
        .insert(data)
        .execute()
    )

    created_pet: dict[str, Any] = response.data[0]

    return created_pet

def get_all_pets_in_adoption(supabase: Client, id_user: str, page: int | None = None) -> list[dict[str, Any]]:
    if page <= 0:
        raise ValueError("El número de página debe ser mayor a 0.")

    query = (
        supabase.table("pets")
        .select("*")
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
    user_profile_response = (
        supabase.table("users_profiles")
        .select(", ".join(USER_CLUSTER_FEATURES + ["preferred_species"]))
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
        .select("*, species:id_breed1(species)")
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

    results = filter(lambda pet: pet["species"]["species"] == user_data["preferred_species"], response.data)

    for pet in response.data:
        if pet["photo_url"] is not None:
            pet["photo_url"] = supabase.storage.from_("avatars").create_signed_url(path=pet["photo_url"], expires_in=60)

    return results