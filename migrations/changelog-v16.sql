
-- liquibase formatted sql
-- changeset Marlon-Leon:1704821121381-16 insert data menu_permission table

INSERT INTO menu_permission (
    id, 
    menu_id, 
    permission_id, 
    state, 
    created_date, 
    updated_date
)
VALUES (
    uuid_generate_v4(), 
    (SELECT id FROM "menu" LIMIT 1),  
    (SELECT id FROM "permission" WHERE name = 'HOME'), 
    TRUE, 
    NOW(), 
    NOW()
);

--ROLLBACK DELETE FROM menu_permission;

