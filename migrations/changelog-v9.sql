--RUN 
--NAME=Marlon Andres Leon Leon
--DESCRIPTION=Crea un permiso para la empresa creada

-- Inserción para el permiso 'UPDATE'
INSERT INTO rol_permission (
    id, 
    rol_id, 
    permission_id, 
    state, 
    created_date, 
    updated_date
)
VALUES (
    uuid_generate_v4(),                       -- Genera un UUID automáticamente para la columna id
    '05afee90-958c-41a8-a25d-193aa55dc2a7',                         -- UUID del rol admin (debe ser reemplazado con el UUID real)
    'eb592629-5e75-4d69-92fb-c8624eb6ee7a',                 -- UUID del permiso 'UPDATE' (debe ser reemplazado con el UUID real)
    TRUE,                                     -- Estado (activo)
    NOW(),                                    -- Fecha de creación
    NOW()                                     -- Fecha de actualización
);

-- Inserción para el permiso 'READ'
INSERT INTO rol_permission (
    id, 
    rol_id, 
    permission_id, 
    state, 
    created_date, 
    updated_date
)
VALUES (
    uuid_generate_v4(),
    '05afee90-958c-41a8-a25d-193aa55dc2a7',                         -- UUID del rol admin
    'afa8e64c-7ab6-4754-b1d6-1ff8fbc79832',                   -- UUID del permiso 'READ'
    TRUE,
    NOW(),
    NOW()
);

-- Inserción para el permiso 'DELETE'
INSERT INTO rol_permission (
    id, 
    rol_id, 
    permission_id, 
    state, 
    created_date, 
    updated_date
)
VALUES (
    uuid_generate_v4(),
    '05afee90-958c-41a8-a25d-193aa55dc2a7',                         -- UUID del rol admin
    '5d52fded-5d1a-4857-aed7-c75b90a001b0',                 -- UUID del permiso 'DELETE'
    TRUE,
    NOW(),
    NOW()
);

-- Inserción para el permiso 'SAVE'
INSERT INTO rol_permission (
    id, 
    rol_id, 
    permission_id, 
    state, 
    created_date, 
    updated_date
)
VALUES (
    uuid_generate_v4(),
    '05afee90-958c-41a8-a25d-193aa55dc2a7',                         -- UUID del rol admin
    '14d27091-ced7-4184-a30e-70ee330cdbfe',                   -- UUID del permiso 'SAVE'
    TRUE,
    NOW(),
    NOW()
);

-- Inserción para el permiso 'LIST'
INSERT INTO rol_permission (
    id, 
    rol_id, 
    permission_id, 
    state, 
    created_date, 
    updated_date
)
VALUES (
    uuid_generate_v4(),
    '05afee90-958c-41a8-a25d-193aa55dc2a7',                         -- UUID del rol admin
    '8e7f3678-29ea-4f49-a764-5b9f54cb8075',                   -- UUID del permiso 'LIST'
    TRUE,
    NOW(),
    NOW()
);


INSERT INTO rol_permission (
    id, 
    rol_id, 
    permission_id, 
    state, 
    created_date, 
    updated_date
)
VALUES (
    uuid_generate_v4(),
    '05afee90-958c-41a8-a25d-193aa55dc2a7',                         -- UUID del rol admin
    '83358927-d5b7-4e3b-8e69-364d00374af6',                   -- UUID del permiso 'HOME'
    TRUE,
    NOW(),
    NOW()
);






--FIN RUN

--ROLLBACK
-- Rollback para el permiso 'UPDATE'
DELETE FROM rol_permission 
WHERE rol_id = '05afee90-958c-41a8-a25d-193aa55dc2a7' 
AND permission_id = 'eb592629-5e75-4d69-92fb-c8624eb6ee7a';

-- Rollback para el permiso 'READ'
DELETE FROM rol_permission 
WHERE rol_id = '05afee90-958c-41a8-a25d-193aa55dc2a7' 
AND permission_id = 'afa8e64c-7ab6-4754-b1d6-1ff8fbc79832';

-- Rollback para el permiso 'DELETE'
DELETE FROM rol_permission 
WHERE rol_id = '05afee90-958c-41a8-a25d-193aa55dc2a7' 
AND permission_id = '5d52fded-5d1a-4857-aed7-c75b90a001b0';

-- Rollback para el permiso 'SAVE'
DELETE FROM rol_permission 
WHERE rol_id = '05afee90-958c-41a8-a25d-193aa55dc2a7' 
AND permission_id = '14d27091-ced7-4184-a30e-70ee330cdbfe';

-- Rollback para el permiso 'LIST'
DELETE FROM rol_permission 
WHERE rol_id = '05afee90-958c-41a8-a25d-193aa55dc2a7' 
AND permission_id = '8e7f3678-29ea-4f49-a764-5b9f54cb8075';

-- Rollback para el permiso 'HOME'
DELETE FROM rol_permission 
WHERE rol_id = '05afee90-958c-41a8-a25d-193aa55dc2a7' 
AND permission_id = '83358927-d5b7-4e3b-8e69-364d00374af6';

--FIN ROLLBACK
