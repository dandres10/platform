--RUN 
--NAME=Marlon Andres Leon Leon
--DESCRIPTION=Crea un permiso para la empresa creada

INSERT INTO currency_location (id, currency_id, location_id, state, created_date, updated_date)
VALUES (
    uuid_generate_v4(), 
    '8773a13c-6e5a-4dc6-986f-58c65468d294',  -- currency_id
    'b7d155b4-dc94-4198-908a-c919d9cff336',  -- location_id
    TRUE, 
    NOW(), 
    NOW()
);

--FIN RUN
--ROLLBACK
DELETE FROM currency_location
WHERE currency_id = '8773a13c-6e5a-4dc6-986f-58c65468d294'
  AND location_id = 'b7d155b4-dc94-4198-908a-c919d9cff336';

--FIN ROLLBACK