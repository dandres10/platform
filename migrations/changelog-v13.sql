--RUN 
--NAME=Marlon Andres Leon Leon
--DESCRIPTION=Crea un permiso para la empresa creada
INSERT INTO
  user_location (
    id,
    user_id,
    location_id,
    state,
    created_date,
    updated_date
  )
VALUES
  (
    uuid_generate_v4 (),
    '7ffc2e72-7923-48cb-8655-0cecdc8bf745', -- user_id
    'b7d155b4-dc94-4198-908a-c919d9cff336', -- location_id
    TRUE,
    NOW (),
    NOW ()
  );

--FIN RUN
--ROLLBACK
DELETE FROM user_location
WHERE
  user_id = '7ffc2e72-7923-48cb-8655-0cecdc8bf745'
  AND location_id = 'b7d155b4-dc94-4198-908a-c919d9cff336';

--FIN ROLLBACK