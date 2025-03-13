
-- liquibase formatted sql
-- changeset Marlon-Leon:1704821121381-18 insert data rol table


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
    (SELECT id FROM rol WHERE code = 'COLLA'),                         
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
    (SELECT id FROM rol WHERE code = 'COLLA'),                         
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
    (SELECT id FROM rol WHERE code = 'COLLA'),                         
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
    (SELECT id FROM rol WHERE code = 'COLLA'),                         
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
    (SELECT id FROM rol WHERE code = 'COLLA'),                         
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
    (SELECT id FROM rol WHERE code = 'COLLA'),                         
    (SELECT id FROM permission WHERE name = 'HOME'),
    TRUE,
    NOW(),
    NOW()
);


--ROLLBACK DELETE FROM rol WHERE code = 'COLLA';

