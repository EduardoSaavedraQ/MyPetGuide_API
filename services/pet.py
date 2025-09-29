from supabase import Client
from typing import Any
from services.image_service import replace_image_profile, upload_image_to_supabase

def create_pet(
        data: dict[str, Any],
        image: bytes | None,
        id_user: str,
        supabase: Client
):
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

    