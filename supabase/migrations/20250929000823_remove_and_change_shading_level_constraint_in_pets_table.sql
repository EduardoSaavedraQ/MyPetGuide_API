ALTER TABLE pets
    DROP CONSTRAINT IF EXISTS pets_shading_level_check,
    ADD CONSTRAINT pets_shedding_level_check CHECK (shedding_level BETWEEN 1 AND 3);

ALTER TABLE pets
    DROP COLUMN IF EXISTS has_other_pets;