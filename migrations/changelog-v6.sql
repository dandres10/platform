-- liquibase formatted sql
-- changeset Marlon-Leon:1704821121381-6 insert data location table

INSERT INTO location (
    id, 
    company_id, 
    country_id, 
    name, 
    address, 
    city, 
    phone, 
    email, 
    main_location, 
    state, 
    created_date, 
    updated_date
)
VALUES (
    uuid_generate_v4(),                  
    (SELECT id FROM company LIMIT 1),  
    (SELECT id FROM country LIMIT 1),
    'Chico',                        
    'carrera 11 # 100',                    
    'Bogota',                         
    '4562323',                        
    'info@klym.com',                   
    TRUE,                                 
    TRUE,                                
    NOW(),                                
    NOW()                                 
);

--ROLLBACK DELETE FROM location WHERE name = 'Chico' AND address = 'carrera 11 # 100';

