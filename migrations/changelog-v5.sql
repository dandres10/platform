-- liquibase formatted sql
-- changeset Marlon-Leon:1704821121381-5 insert data country table

INSERT INTO country (
    id, 
    name, 
    code, 
    phone_code, 
    state, 
    created_date, 
    updated_date
)
VALUES (
    uuid_generate_v4(),   
    'Colombia',           
    'CO',                 
    '+57',                
    TRUE,                 
    NOW(),                
    NOW()                 
);



--ROLLBACK DELETE FROM country WHERE code = 'CO';

