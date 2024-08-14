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
    '969961a3-3492-45a5-8f8d-b283e52e99ee',                         -- UUID del rol admin (debe ser reemplazado con el UUID real)
    'ab8ba371-14c4-46e4-b513-f2bf11bda579',                 -- UUID del permiso 'UPDATE' (debe ser reemplazado con el UUID real)
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
    '969961a3-3492-45a5-8f8d-b283e52e99ee',                         -- UUID del rol admin
    'd9b0aaa2-346a-4c51-b703-1019aba44469',                   -- UUID del permiso 'READ'
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
    '969961a3-3492-45a5-8f8d-b283e52e99ee',                         -- UUID del rol admin
    '6702efd0-412d-4002-ab1f-d88e08d572d5',                 -- UUID del permiso 'DELETE'
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
    '969961a3-3492-45a5-8f8d-b283e52e99ee',                         -- UUID del rol admin
    'a41f0727-abdf-4b07-a988-40998a868547',                   -- UUID del permiso 'SAVE'
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
    '969961a3-3492-45a5-8f8d-b283e52e99ee',                         -- UUID del rol admin
    'be273874-1f6f-4e0f-bb70-e86bf02e4ba8',                   -- UUID del permiso 'LIST'
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
    '969961a3-3492-45a5-8f8d-b283e52e99ee',                         -- UUID del rol admin
    'c9cee9bc-4bea-4431-a77b-70a7538e8409',                   -- UUID del permiso 'HOME'
    TRUE,
    NOW(),
    NOW()
);






--FIN RUN

--ROLLBACK
-- Rollback para el permiso 'UPDATE'
DELETE FROM rol_permission 
WHERE rol_id = '969961a3-3492-45a5-8f8d-b283e52e99ee' 
AND permission_id = 'ab8ba371-14c4-46e4-b513-f2bf11bda579';

-- Rollback para el permiso 'READ'
DELETE FROM rol_permission 
WHERE rol_id = '969961a3-3492-45a5-8f8d-b283e52e99ee' 
AND permission_id = 'd9b0aaa2-346a-4c51-b703-1019aba44469';

-- Rollback para el permiso 'DELETE'
DELETE FROM rol_permission 
WHERE rol_id = '969961a3-3492-45a5-8f8d-b283e52e99ee' 
AND permission_id = '6702efd0-412d-4002-ab1f-d88e08d572d5';

-- Rollback para el permiso 'SAVE'
DELETE FROM rol_permission 
WHERE rol_id = '969961a3-3492-45a5-8f8d-b283e52e99ee' 
AND permission_id = 'a41f0727-abdf-4b07-a988-40998a868547';

-- Rollback para el permiso 'LIST'
DELETE FROM rol_permission 
WHERE rol_id = '969961a3-3492-45a5-8f8d-b283e52e99ee' 
AND permission_id = 'be273874-1f6f-4e0f-bb70-e86bf02e4ba8';

--FIN ROLLBACK
