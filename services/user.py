from sqlmodel import UUID
from schemas.users import UserCreate, UserRead
from services.image_service import upload_image_to_supabase
from supabase import Client

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