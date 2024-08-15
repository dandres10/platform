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
    '83950f65-ae93-4214-b5b1-8ccd479180b3', -- UUID de la compañía (debe existir en la tabla company)
    'Admin',                                -- Nombre del rol
    'ADMIN',                                -- Código único para el rol
    'core_rol_admin',  -- Descripción del rol
    TRUE,                                   -- Estado (activo)
    NOW(),                                  -- Fecha de creación
    NOW()                                   -- Fecha de actualización
);


--FIN RUN

--ROLLBACK
DELETE FROM rol WHERE code = 'ADMIN' AND company_id = '83950f65-ae93-4214-b5b1-8ccd479180b3';
--FIN ROLLBACK
