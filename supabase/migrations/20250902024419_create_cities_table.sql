CREATE TABLE IF NOT EXISTS cities (
    id_city CHAR(5) PRIMARY KEY,
    id_state CHAR(2) NOT NULL REFERENCES states(id_state),
    city_name VARCHAR(100) NOT NULL CHECK(TRIM(city_name) <> '')
)