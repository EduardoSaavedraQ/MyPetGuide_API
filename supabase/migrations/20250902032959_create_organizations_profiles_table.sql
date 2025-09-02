CREATE TABLE IF NOT EXISTS organizations_profiles (
    id_organization BIGSERIAL PRIMARY KEY,
    id_user UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
    organization_name VARCHAR(255) NOT NULL UNIQUE CHECK (TRIM(organization_name) <> ''),
    photo_url VARCHAR(255) CHECK (TRIM(photo_url) <> ''),
    biography TEXT CHECK (TRIM(biography) <> ''),
    admin_first_name VARCHAR(50) NOT NULL CHECK (TRIM(admin_first_name) <> ''),
    admin_last_name VARCHAR(50) NOT NULL CHECK (TRIM(admin_last_name) <> ''),
    admin_sLast_name VARCHAR(50) CHECK (TRIM(admin_sLast_name) <> '')
);