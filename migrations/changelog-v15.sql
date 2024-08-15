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
    'a1adc7de-3f83-43f4-863d-a689f5e544f5',  -- menu_id
    '83358927-d5b7-4e3b-8e69-364d00374af6',  -- permission_id
    TRUE, 
    NOW(), 
    NOW()
);

--FIN RUN
--ROLLBACK
DELETE FROM menu_permission
WHERE menu_id = 'a1adc7de-3f83-43f4-863d-a689f5e544f5'
  AND permission_id = '83358927-d5b7-4e3b-8e69-364d00374af6';

--FIN ROLLBACK