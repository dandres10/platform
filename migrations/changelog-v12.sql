-- liquibase formatted sql
-- changeset Marlon-Leon:1704821121381-12 insert data platform table

INSERT INTO
  platform (
    id,
    language_id,
    location_id,
    currency_id,
    token_expiration_minutes,
    refresh_token_expiration_minutes,
    created_date,
    updated_date
  )
VALUES
  (
    uuid_generate_v4 (),
    (SELECT id FROM "language" LIMIT 1), 
    (SELECT id FROM "location" LIMIT 1),
    (SELECT id FROM "currency" LIMIT 1),
    60, 
    62,
    NOW (),
    NOW ()
  );


--ROLLBACK DELETE FROM platform;

