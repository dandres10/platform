-- liquibase formatted sql
-- changeset make-platform-location-optional:1731188400000-26


ALTER TABLE platform
ALTER COLUMN location_id DROP NOT NULL;


--ROLLBACK ALTER TABLE platform ALTER COLUMN location_id SET NOT NULL;

