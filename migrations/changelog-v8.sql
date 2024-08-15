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
    '83950f65-ae93-4214-b5b1-8ccd479180b3', -- UUID de la compañía (debe existir en la tabla company)
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
    '83950f65-ae93-4214-b5b1-8ccd479180b3', -- UUID de la compañía (debe existir en la tabla company)
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
    '83950f65-ae93-4214-b5b1-8ccd479180b3', -- UUID de la compañía (debe existir en la tabla company)
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
    '83950f65-ae93-4214-b5b1-8ccd479180b3', -- UUID de la compañía (debe existir en la tabla company)
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
    '83950f65-ae93-4214-b5b1-8ccd479180b3', -- UUID de la compañía (debe existir en la tabla company)
    'LIST',                       -- Nombre del permiso (debe ser único)
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
    '83950f65-ae93-4214-b5b1-8ccd479180b3', -- UUID de la compañía (debe existir en la tabla company)
    'HOME',                       -- Nombre del permiso (debe ser único)
    'Permite al usuario consultar ese item del menu', -- Descripción del permiso
    TRUE,                                   -- Estado (activo)
    NOW(),                                  -- Fecha de creación
    NOW()                                   -- Fecha de actualización
);



--FIN RUN

--ROLLBACK
DELETE FROM permission WHERE name = 'UPDATE' AND company_id = '83950f65-ae93-4214-b5b1-8ccd479180b3';
DELETE FROM permission WHERE name = 'READ' AND company_id = '83950f65-ae93-4214-b5b1-8ccd479180b3';
DELETE FROM permission WHERE name = 'SAVE' AND company_id = '83950f65-ae93-4214-b5b1-8ccd479180b3';
DELETE FROM permission WHERE name = 'DELETE' AND company_id = '83950f65-ae93-4214-b5b1-8ccd479180b3';
DELETE FROM permission WHERE name = 'LIST' AND company_id = '83950f65-ae93-4214-b5b1-8ccd479180b3';
DELETE FROM permission WHERE name = 'HOME' AND company_id = '83950f65-ae93-4214-b5b1-8ccd479180b3';
--FIN ROLLBACK
