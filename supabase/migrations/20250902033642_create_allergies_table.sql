CREATE TABLE IF NOT EXISTS allergies (
    id_allergy BIGSERIAL PRIMARY KEY,
    allergy_name VARCHAR(50) NOT NULL UNIQUE CHECK (TRIM(allergy_name) <> '')
);