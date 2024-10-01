-- liquibase formatted sql
-- changeset Marlon-Leon:1704821121381-11 insert data currency_location table

INSERT INTO currency_location (id, currency_id, location_id, state, created_date, updated_date)
VALUES (
    uuid_generate_v4(), 
    (SELECT id FROM currency LIMIT 1), 
    (SELECT id FROM "location" LIMIT 1),  
    TRUE, 
    NOW(), 
    NOW()
);

--ROLLBACK DELETE FROM currency_location;