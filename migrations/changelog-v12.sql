--RUN 
--NAME=Marlon Andres Leon Leon
--DESCRIPTION=Crea un permiso para la empresa creada
INSERT INTO
  platform (
    id,
    language_id,
    location_id,
    currency_location_id,
    token_expiration_minutes,
    refresh_token_expiration_minutes,
    created_date,
    updated_date
  )
VALUES
  (
    uuid_generate_v4 (),
    '1e33b3ee-19c3-4a96-beee-3564d1bf12b9', -- language_id
    'b7d155b4-dc94-4198-908a-c919d9cff336', -- location_id
    '0774616f-c038-4479-a623-7f963d4993e8', -- currency_location_id
    60, -- token_expiration_minutes
    62, -- refresh_token_expiration_minutes
    NOW (),
    NOW ()
  );

--FIN RUN
--ROLLBACK
DELETE FROM platform
WHERE
  language_id = '1e33b3ee-19c3-4a96-beee-3564d1bf12b9'
  AND location_id = 'b7d155b4-dc94-4198-908a-c919d9cff336'
  AND currency_location_id = '0774616f-c038-4479-a623-7f963d4993e8';

--FIN ROLLBACK