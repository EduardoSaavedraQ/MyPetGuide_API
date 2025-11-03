Create or replace function transfer_pet_ownership(
    pet_id BIGINT,
    old_owner UUID,
    new_owner UUID
) RETURNS void as $$
BEGIN
    INSERT INTO addoptions(id_pet, id_prev_owner, id_new_owner)
    VALUES (pet_id, old_owner, new_owner);

    UPDATE pets
    SET id_owner = new_owner
    WHERE id_pet = pet_id;
    
    UPDATE chat_rooms
    SET finished = true
    WHERE id_pet = pet_id;
END;
$$ language plpgsql security definer;