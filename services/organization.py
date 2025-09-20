from sqlmodel import UUID, Session
from schemas.organizations import OrganizationCreate
from services.image_service import upload_image_to_supabase
from supabase import Client
from schemas.organizations import OrganizationCreate
from models.organization_profile import OrganizationProfile
from utils.db import get_engine

def create_organization_db(supabase: Client, organization_profile: OrganizationCreate, user_id: UUID, image: bytes | None = None) -> OrganizationProfile:
    organization_db = OrganizationProfile(**organization_profile.model_dump(), id_user=user_id)

    if image is not None:
        response = upload_image_to_supabase(id=user_id, image=image, bucket="avatars", path="public/organizations", supabase=supabase)

        organization_db.photo_url = response.path

    with Session(get_engine()) as session:
        session.add(organization_db)
        session.commit()
        session.refresh(organization_db)

    return organization_db