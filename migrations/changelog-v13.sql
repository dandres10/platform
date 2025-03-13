

-- liquibase formatted sql
-- changeset Marlon-Leon:1704821121381-13 insert data user table

INSERT INTO "user" (platform_id, password, email, first_name, last_name, phone, refresh_token,  created_date,
    updated_date)
VALUES (
    (SELECT id FROM "platform" LIMIT 1),         
    '$2b$12$.BsJdi.jmp2AivooGAn7FOEazabWXg/mP04ciMEr8MUh3J9f4jKNm',             
    'marlon@goluti.com',         
    'Marlon',                        
    'Leon',                         
    '234567890',                 
    NULL,
    NOW (),
    NOW ()
);



--ROLLBACK DELETE FROM "user";