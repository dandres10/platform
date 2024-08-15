--RUN 
--NAME=Marlon Andres Leon Leon
--DESCRIPTION= Se de crear el usuario primero
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
    '7979c956-0e2e-4d4a-b6e6-e12d6567eba5', -- user_id
    '05afee90-958c-41a8-a25d-193aa55dc2a7', -- rol_id
    'f5ccc80f-aa1e-4775-a610-0d9a3bd44e18', -- location_id
    TRUE,
    NOW (),
    NOW ()
  );

--FIN RUN
--ROLLBACK
DELETE FROM user_location_rol
WHERE
  user_id = '7979c956-0e2e-4d4a-b6e6-e12d6567eba5'
  AND location_id = 'f5ccc80f-aa1e-4775-a610-0d9a3bd44e18'
  AND rol_id = '05afee90-958c-41a8-a25d-193aa55dc2a7';

--FIN ROLLBACK