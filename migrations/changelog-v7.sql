-- liquibase formatted sql
-- changeset Marlon-Leon:1704821121381-7 insert data rol table

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
    uuid_generate_v4(),                     
    (SELECT id FROM company LIMIT 1), 
    'Admin',                                
    'ADMIN',                                
    'core_rol_admin',  
    TRUE,                                   
    NOW(),                                  
    NOW()                                   
);




--ROLLBACK DELETE FROM rol;

