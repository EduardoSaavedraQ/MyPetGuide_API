CREATE TABLE IF NOT EXISTS chat_messages(
    id_message BIGSERIAL PRIMARY KEY,
    id_room BIGINT NOT NULL REFERENCES chat_rooms(id_room),
    id_sender UUID NOT NULL REFERENCES auth.users(id),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);