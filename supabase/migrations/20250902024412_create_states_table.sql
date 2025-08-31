CREATE TABLE IF NOT EXISTS states (
    id_state CHAR(2) PRIMARY KEY,
    state_name VARCHAR(50) NOT NULL CHECK (TRIM(state_name) <> '')
)