--RUN 
--NAME=Marlon Andres Leon Leon
--DESCRIPTION=Crea un rol para la empresa creada

INSERT INTO rol (
    id, 
    company_id, 
    name, 
    code, 
    description, 
    state, 
    created_date, 
    updated_date
)
VALUES (
    uuid_generate_v4(),                     -- Genera un UUID automáticamente para la columna id
    'd5c552fb-9434-4301-83af-03f3ca4195cf', -- UUID de la compañía (debe existir en la tabla company)
    'Admin',                                -- Nombre del rol
    'ADMIN',                                -- Código único para el rol
    'core_rol_admin',  -- Descripción del rol
    TRUE,                                   -- Estado (activo)
    NOW(),                                  -- Fecha de creación
    NOW()                                   -- Fecha de actualización
);


--FIN RUN

--ROLLBACK
DELETE FROM rol WHERE code = 'ADMIN' AND company_id = 'd5c552fb-9434-4301-83af-03f3ca4195cf';
--FIN ROLLBACK
