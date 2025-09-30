ALTER TABLE pets
    DROP CONSTRAINT IF EXISTS pets_shedding_level_check,
    ADD CONSTRAINT pets_shedding_level_check CHECK (
        (fur_length = 0 AND shedding_level = 0) OR
        (fur_length != 0 AND shedding_level BETWEEN 1 AND 3)
    );

