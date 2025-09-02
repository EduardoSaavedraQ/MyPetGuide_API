CREATE TABLE IF NOT EXISTS user_has_allergies (
    id BIGSERIAL PRIMARY KEY,
    id_profile BIGINT NOT NULL REFERENCES users_profiles(id_profile) ON DELETE CASCADE,
    id_allergy BIGINT NOT NULL REFERENCES allergies(id_allergy) ON DELETE CASCADE,
    UNIQUE(id_profile, id_allergy)
);