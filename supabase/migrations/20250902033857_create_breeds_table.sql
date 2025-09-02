CREATE TABLE IF NOT EXISTS breeds (
    id_breed SERIAL PRIMARY KEY,
    species BOOLEAN NOT NULL,
    breed_name VARCHAR(100) NOT NULL UNIQUE CHECK (TRIM(breed_name) <> '')
);