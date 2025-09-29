from sqlmodel import UUID
from schemas.organizations import OrganizationCreate, OrganizationRead
from services.image_service import upload_image_to_supabase
from supabase import Client
from typing import Any

def create_organization_db(supabase: Client, organization_profile: OrganizationCreate, id_user: UUID, image: bytes | None = None) -> OrganizationRead:
    data_to_insert: dict = organization_profile.model_dump(include={
                                "organization_name",
                                "admin_first_name",
                                "admin_last_name",
                                "admin_slast_name",
                                "biography"
                            })

    data_to_insert["id_user"] = id_user

    response = (
        supabase.table("organizations_profiles")
        .insert(data_to_insert)
        .execute()
    )

    created_organization: OrganizationRead = OrganizationRead(**response.data[0])

    if image is not None:
        upload_response = upload_image_to_supabase(id=id_user, image=image, bucket="avatars", path="public/organizations", supabase=supabase)

        update_response = (
            supabase.table("organizations_profiles")
            .update({"photo_url": upload_response.path})
            .eq("id_organization", created_organization.id_organization)
            .execute()
        )

        created_organization.photo_url = upload_response.path

    return created_organization

def get_organization_all_data(supabase: Client, id_user: str) -> dict[str, Any]:

    organization_query_response: dict = (
        supabase.table("organizations_profiles")
        .select("*")
        .eq("id_user", id_user)
        .execute()
    )

    organization_data: dict = organization_query_response.data[0] if organization_query_response.data else dict()

    pet_query_response = (
        supabase.table("pets")
        .select("*")
        .eq("id_owner", id_user)
        .execute()
    )

    organization_pets: dict = pet_query_response.data

    return {
        "organization": organization_data,
        "pets": organization_pets
    }