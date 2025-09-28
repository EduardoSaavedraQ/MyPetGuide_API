from sqlmodel import UUID
from schemas.users import UserCreate, UserRead
from services.image_service import upload_image_to_supabase, replace_image_profile
from supabase import Client
from services.ml.kmeans_service import predict_cluster
from utils.user import USER_CLUSTER_FEATURES, can_clusterize, transform_bool_cluster_features_to_int
from services.ml.kmeans_service import predict_cluster

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
        features = [data_to_update[field] for field in USER_CLUSTER_FEATURES]
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