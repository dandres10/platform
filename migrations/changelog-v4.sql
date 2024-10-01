-- liquibase formatted sql
-- changeset Marlon-Leon:1704821121381-4 insert data company table

INSERT INTO company (id, name, inactivity_time, nit, state, created_date, updated_date)
VALUES (
    uuid_generate_v4(),         
    'Klym',          
    30,                         
    '123456789',                
    TRUE,                       
    NOW(),                      
    NOW()                       
);

--ROLLBACK DELETE FROM company WHERE nit = '123456789';
