-- liquibase formatted sql
-- changeset Marlon-Leon:1704821121381-14 insert data user_location_rol table

INSERT INTO
  user_location_rol (
    id,
    user_id,
    rol_id,
    location_id,
    state,
    created_date,
    updated_date
  )
VALUES
  (
    uuid_generate_v4 (),
    (SELECT id FROM "user" LIMIT 1), 
    (SELECT id FROM "rol" LIMIT 1), 
    (SELECT id FROM "location" LIMIT 1), 
    TRUE,
    NOW (),
    NOW ()
  );


--ROLLBACK DELETE FROM user_location_rol;