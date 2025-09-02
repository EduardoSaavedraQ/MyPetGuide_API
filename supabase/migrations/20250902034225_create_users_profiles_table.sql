CREATE TABLE IF NOT EXISTS users_profiles (
    id_profile BIGSERIAL PRIMARY KEY,
    id_user UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
    photo_url VARCHAR(255) CHECK (TRIM(photo_url) <> ''),
    first_name VARCHAR(50) NOT NULL CHECK (TRIM(first_name) <> ''),
    last_name VARCHAR(50) NOT NULL CHECK (TRIM(last_name) <> ''),
    sLast_name VARCHAR(50) CHECK (TRIM(sLast_name) <> ''),
    house_size SMALLINT,
    house_backyard_size SMALLINT,
    family_size SMALLINT CHECK (family_size >= 1),
    has_kids BOOLEAN,
    has_neighbors BOOLEAN,
    available_time_per_day SMALLINT CHECK (available_time_per_day >= 1 AND available_time_per_day <= 24),
    vet_accesss BOOLEAN,
    has_other_pets BOOLEAN,
    experience_with_pets SMALLINT,
    preferred_species BOOLEAN
);