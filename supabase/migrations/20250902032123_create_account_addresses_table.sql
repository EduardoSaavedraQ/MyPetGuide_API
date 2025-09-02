CREATE TABLE IF NOT EXISTS account_addresses (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    city_id CHAR(5) NOT NULL REFERENCES cities(id_city),
    address VARCHAR(255) CHECK (TRIM(address) <> ''),
    postal_code CHAR(5) CHECK (LENGTH(postal_code) = 5)
);