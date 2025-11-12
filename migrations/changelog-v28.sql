-- liquibase formatted sql
-- changeset make-menu-company-id-optional:1731445200000-28


ALTER TABLE menu
ALTER COLUMN company_id DROP NOT NULL;


--ROLLBACK ALTER TABLE menu ALTER COLUMN company_id SET NOT NULL;

