CREATE TABLE IF NOT EXISTS chat_rooms(
    id_room BIGSERIAL PRIMARY KEY,
    id_pet BIGINT NOT NULL REFERENCES pets,
    id_requester UUID NOT NULL REFERENCES auth.users(id),
    id_owner UUID NOT NULL REFERENCES auth.users(id) CHECK(id_owner != id_requester),
    finished BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT unique_chat_per_pet_and_requester UNIQUE (id_pet, id_requester)
);