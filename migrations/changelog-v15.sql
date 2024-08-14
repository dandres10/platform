--RUN 
--NAME=Marlon Andres Leon Leon
--DESCRIPTION=Crea un permiso para la empresa creada
INSERT INTO menu_permission (
    id, 
    menu_id, 
    permission_id, 
    state, 
    created_date, 
    updated_date
)
VALUES (
    uuid_generate_v4(), 
    '634eb539-a758-4f21-9d14-eb1f04cdaca1',  -- menu_id
    'f2b1a5c4-89a1-4b5b-b7f8-6a3b7d4c1e7d',  -- permission_id
    TRUE, 
    NOW(), 
    NOW()
);

--FIN RUN
--ROLLBACK
DELETE FROM menu_permission
WHERE menu_id = '634eb539-a758-4f21-9d14-eb1f04cdaca1'
  AND permission_id = 'f2b1a5c4-89a1-4b5b-b7f8-6a3b7d4c1e7d';

--FIN ROLLBACK