from sqlmodel import UUID
from schemas.organizations import OrganizationCreate, OrganizationRead
from services.image_service import upload_image_to_supabase
from supabase import Client
from schemas.organizations import OrganizationCreate

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