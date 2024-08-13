--RUN 
--NAME=Marlon Andres Leon Leon
--DESCRIPTION=Crea un permiso para la empresa creada

INSERT INTO permission (
    id, 
    company_id, 
    name, 
    description, 
    state, 
    created_date, 
    updated_date
)
VALUES (
    uuid_generate_v4(),                     -- Genera un UUID automáticamente para la columna id
    'd5c552fb-9434-4301-83af-03f3ca4195cf', -- UUID de la compañía (debe existir en la tabla company)
    'UPDATE',                       -- Nombre del permiso (debe ser único)
    'Permite al usuario actualizar en la api', -- Descripción del permiso
    TRUE,                                   -- Estado (activo)
    NOW(),                                  -- Fecha de creación
    NOW()                                   -- Fecha de actualización
);

INSERT INTO permission (
    id, 
    company_id, 
    name, 
    description, 
    state, 
    created_date, 
    updated_date
)
VALUES (
    uuid_generate_v4(),                     -- Genera un UUID automáticamente para la columna id
    'd5c552fb-9434-4301-83af-03f3ca4195cf', -- UUID de la compañía (debe existir en la tabla company)
    'READ',                       -- Nombre del permiso (debe ser único)
    'Permite al usuario consultar en la api', -- Descripción del permiso
    TRUE,                                   -- Estado (activo)
    NOW(),                                  -- Fecha de creación
    NOW()                                   -- Fecha de actualización
);

INSERT INTO permission (
    id, 
    company_id, 
    name, 
    description, 
    state, 
    created_date, 
    updated_date
)
VALUES (
    uuid_generate_v4(),                     -- Genera un UUID automáticamente para la columna id
    'd5c552fb-9434-4301-83af-03f3ca4195cf', -- UUID de la compañía (debe existir en la tabla company)
    'DELETE',                       -- Nombre del permiso (debe ser único)
    'Permite al usuario consultar en la api', -- Descripción del permiso
    TRUE,                                   -- Estado (activo)
    NOW(),                                  -- Fecha de creación
    NOW()                                   -- Fecha de actualización
);

INSERT INTO permission (
    id, 
    company_id, 
    name, 
    description, 
    state, 
    created_date, 
    updated_date
)
VALUES (
    uuid_generate_v4(),                     -- Genera un UUID automáticamente para la columna id
    'd5c552fb-9434-4301-83af-03f3ca4195cf', -- UUID de la compañía (debe existir en la tabla company)
    'SAVE',                       -- Nombre del permiso (debe ser único)
    'Permite al usuario consultar en la api', -- Descripción del permiso
    TRUE,                                   -- Estado (activo)
    NOW(),                                  -- Fecha de creación
    NOW()                                   -- Fecha de actualización
);

INSERT INTO permission (
    id, 
    company_id, 
    name, 
    description, 
    state, 
    created_date, 
    updated_date
)
VALUES (
    uuid_generate_v4(),                     -- Genera un UUID automáticamente para la columna id
    'd5c552fb-9434-4301-83af-03f3ca4195cf', -- UUID de la compañía (debe existir en la tabla company)
    'LIST',                       -- Nombre del permiso (debe ser único)
    'Permite al usuario consultar en la api', -- Descripción del permiso
    TRUE,                                   -- Estado (activo)
    NOW(),                                  -- Fecha de creación
    NOW()                                   -- Fecha de actualización
);





--FIN RUN

--ROLLBACK
DELETE FROM permission WHERE name = 'UPDATE' AND company_id = 'd5c552fb-9434-4301-83af-03f3ca4195cf';
DELETE FROM permission WHERE name = 'READ' AND company_id = 'd5c552fb-9434-4301-83af-03f3ca4195cf';
DELETE FROM permission WHERE name = 'SAVE' AND company_id = 'd5c552fb-9434-4301-83af-03f3ca4195cf';
DELETE FROM permission WHERE name = 'DELETE' AND company_id = 'd5c552fb-9434-4301-83af-03f3ca4195cf';
DELETE FROM permission WHERE name = 'LIST' AND company_id = 'd5c552fb-9434-4301-83af-03f3ca4195cf';
--FIN ROLLBACK
