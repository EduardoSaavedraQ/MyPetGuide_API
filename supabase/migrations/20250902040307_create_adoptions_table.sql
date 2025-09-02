CREATE TABLE IF NOT EXISTS addoptions (
    id_adoption BIGSERIAL PRIMARY KEY,
    id_pet BIGINT NOT NULL REFERENCES pets(id_pet),
    id_prev_owner UUID NOT NULL REFERENCES auth.users(id),
    id_new_owner UUID NOT NULL REFERENCES auth.users(id),
    adoption_reason TEXT CHECK (TRIM(adoption_reason) <> ''),
    adoption_date DATE NOT NULL DEFAULT CURRENT_DATE
);