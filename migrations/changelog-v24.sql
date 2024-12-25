-- liquibase formatted sql
-- changeset Marlon-Leon:1704821121381-24 


ALTER TABLE "user"
ADD COLUMN identification VARCHAR(30) NOT NULL DEFAULT '0000000000';

ALTER TABLE "user"
ALTER COLUMN identification DROP DEFAULT;



--ROLLBACK ALTER TABLE "user" DROP COLUMN identification;