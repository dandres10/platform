-- liquibase formatted sql
-- changeset Marlon-Leon:1704821121381-8 insert data permission table

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
    uuid_generate_v4(),                     
    NULL, 
    'UPDATE',                       
    'Permite al usuario actualizar en la api', 
    TRUE,                                   
    NOW(),                                  
    NOW()                                   
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
    uuid_generate_v4(),                     
    NULL, 
    'READ',                       
    'Permite al usuario consultar en la api', 
    TRUE,                                   
    NOW(),                                  
    NOW()                                   
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
    uuid_generate_v4(),                     
    NULL, 
    'DELETE',                       
    'Permite al usuario consultar en la api', 
    TRUE,                                   
    NOW(),                                  
    NOW()                                   
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
    uuid_generate_v4(),                     
    NULL, 
    'SAVE',                       
    'Permite al usuario consultar en la api', 
    TRUE,                                   
    NOW(),                                  
    NOW()                                   
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
    uuid_generate_v4(),                     
    NULL, 
    'LIST',                       
    'Permite al usuario consultar en la api', 
    TRUE,                                   
    NOW(),                                  
    NOW()                                   
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
    uuid_generate_v4(),                     
    NULL, 
    'HOME',                       
    'Permite al usuario consultar ese item del menu', 
    TRUE,                                   
    NOW(),                                  
    NOW()                                   
);


--ROLLBACK DELETE FROM permission;

