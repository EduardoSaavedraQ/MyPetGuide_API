CREATE TABLE IF NOT EXISTS compatibilities (
    id_compatibility BIGSERIAL PRIMARY KEY,
    id_profile BIGINT NOT NULL REFERENCES users_profiles(id_profile),
    id_pet BIGINT NOT NULL REFERENCES pets(id_pet),
    compatibility SMALLINT NOT NULL CHECK (compatibility BETWEEN 1 AND 5),
    evaluation_date DATE NOT NULL DEFAULT CURRENT_DATE
);