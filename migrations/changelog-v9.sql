-- liquibase formatted sql
-- changeset Marlon-Leon:1704821121381-9 insert data rol_permission table


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
    (SELECT id FROM rol LIMIT 1),                         
    (SELECT id FROM permission WHERE name = 'UPDATE'),                 
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
    (SELECT id FROM rol LIMIT 1),                         
    (SELECT id FROM permission WHERE name = 'READ'),
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
    (SELECT id FROM rol LIMIT 1),                         
    (SELECT id FROM permission WHERE name = 'DELETE'),
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
    (SELECT id FROM rol LIMIT 1),                         
    (SELECT id FROM permission WHERE name = 'SAVE'),
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
    (SELECT id FROM rol LIMIT 1),                         
    (SELECT id FROM permission WHERE name = 'LIST'),
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
    (SELECT id FROM rol LIMIT 1),                         
    (SELECT id FROM permission WHERE name = 'HOME'),
    TRUE,
    NOW(),
    NOW()
);


--ROLLBACK DELETE FROM rol_permission;


