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
    'fd339c29-e973-48d7-9ae7-56fae7eeaca8', -- language_id
    'f5ccc80f-aa1e-4775-a610-0d9a3bd44e18', -- location_id
    'cf82d1de-76e3-420c-92c2-d4bcac2c6d9a', -- currency_location_id
    60, -- token_expiration_minutes
    62, -- refresh_token_expiration_minutes
    NOW (),
    NOW ()
  );

--FIN RUN
--ROLLBACK
DELETE FROM platform
WHERE
  language_id = 'fd339c29-e973-48d7-9ae7-56fae7eeaca8'
  AND location_id = 'f5ccc80f-aa1e-4775-a610-0d9a3bd44e18'
  AND currency_location_id = '0774616f-c038-4479-a623-7f963d4993e8';

--FIN ROLLBACK