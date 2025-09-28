ALTER TABLE breeds
DROP CONSTRAINT breeds_breed_name_key;

ALTER TABLE breeds
ADD CONSTRAINT breeds_species_breed_name_key UNIQUE (species, breed_name);
