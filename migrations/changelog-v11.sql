--RUN 
--NAME=Marlon Andres Leon Leon
--DESCRIPTION=Crea un permiso para la empresa creada

INSERT INTO currency_location (id, currency_id, location_id, state, created_date, updated_date)
VALUES (
    uuid_generate_v4(), 
    '761a7df0-d629-4c67-a186-a50bdfbf2d6e',  -- currency_id
    'f5ccc80f-aa1e-4775-a610-0d9a3bd44e18',  -- location_id
    TRUE, 
    NOW(), 
    NOW()
);

--FIN RUN
--ROLLBACK
DELETE FROM currency_location
WHERE currency_id = '761a7df0-d629-4c67-a186-a50bdfbf2d6e'
  AND location_id = 'f5ccc80f-aa1e-4775-a610-0d9a3bd44e18';

--FIN ROLLBACK