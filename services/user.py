from sqlmodel import UUID
from schemas.users import UserCreate, UserRead
from services.image_service import upload_image_to_supabase, replace_image_profile
from supabase import Client
from services.ml.kmeans_service import predict_cluster
from utils.user import USER_FEAUTURES_TO_SCALE, USER_BOOL_FEATURES, can_clusterize, transform_bool_cluster_features_to_int
from services.ml.scaler_service import scale_data
from typing import Any

def create_user_db(supabase: Client, user_profile: UserCreate, id_user: UUID, image: bytes | None = None) -> UserRead:
    data_to_insert: dict = user_profile.model_dump(include={
                                "first_name",
                                "last_name",
                                "slast_name"
                            })
    
    data_to_insert["id_user"] = id_user

    response = (
        supabase.table("users_profiles")
        .insert(data_to_insert)
        .execute()
    )

    created_user: UserRead = UserRead(**response.data[0])

    if image is not None:
        upload_response = upload_image_to_supabase(id=id_user, image=image, bucket="avatars", path="public/users", supabase=supabase)

        update_response = (
            supabase.table("users_profiles")
            .update({"photo_url": upload_response.path})
            .eq("id_user", created_user.id_user)
            .execute()
        )

        created_user.photo_url = upload_response.path

    return created_user

def update_user_profile(
    supabase: Client,
    id_user: UUID,
    data_to_update: dict,
    image: bytes | None = None
) -> UserRead:
    # Procesar imagen si existe
    if image is not None:
        # Si ya hay foto, reemplazar; si no, subir nueva
        if data_to_update.get("photo_url"):
            upload_response = replace_image_profile(
                id=id_user, image=image, bucket="avatars", path="public/users", supabase=supabase
            )
        else:
            upload_response = upload_image_to_supabase(
                id=id_user, image=image, bucket="avatars", path="public/users", supabase=supabase
            )
        data_to_update["photo_url"] = upload_response.path

    if can_clusterize(data_to_update):
        data_to_update = transform_bool_cluster_features_to_int(data_to_update)
        bool_features = [data_to_update[field] for field in USER_BOOL_FEATURES]
        features_to_scale = [data_to_update[field] for field in USER_FEAUTURES_TO_SCALE]
        scaled_data = scale_data("owner", features_to_scale)
        features = scaled_data[0] + bool_features
        cluster = predict_cluster("owner", features)
        data_to_update["owner_label"] = cluster[0]  # O int(cluster[0])

    # Actualizar todo en una sola consulta
    response = (
        supabase.table("users_profiles")
        .update(data_to_update)
        .eq("id_user", id_user)
        .execute()
    )

    updated_user: UserRead = UserRead(**response.data[0])
    return updated_user

def get_user_all_data(supabase: Client, id_user: str) -> dict[str, Any]:

    user_query_response: dict = (
        supabase.table("users_profiles")
        .select("*")
        .eq("id_user", id_user)
        .execute()
    )

    user_data: dict = user_query_response.data[0] if user_query_response.data else dict()

    user_data["photo_url"] = supabase.storage.from_("avatars").create_signed_url(path=user_data["photo_url"], expires_in=3600)

    pet_query_response = (
        supabase.table("pets")
        .select("*")
        .eq("id_owner", id_user)
        .execute()
    )

    user_pets: dict = pet_query_response.data

    for pet in user_pets:
        if pet["photo_url"] is not None:
            pet["photo_url"] = supabase.storage.from_("avatars").create_signed_url(path=pet["photo_url"], expires_in=3600)

    return {
        "user": user_data,
        "pets": user_pets
    }