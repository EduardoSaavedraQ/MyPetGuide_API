from sqlmodel import SQLModel, Field
from uuid import UUID

class OrganizationProfile(SQLModel, table=True):
    __tablename__ = "organizations_profiles"

    id_organization: int | None = Field(default=None, primary_key=True)
    id_user: UUID = Field(unique=True, index=True)
    organization_name: str = Field(unique=True, index=True)
    photo_url: str | None = None
    biography: str | None = None
    admin_first_name: str
    admin_last_name: str
    admin_slast_name: str | None = None

    def get_admin_full_name(self) -> str:
        return f"{self.admin_first_name} {self.admin_last_name} {self.admin_slast_name}"