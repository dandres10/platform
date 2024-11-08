-- liquibase formatted sql
-- changeset Marlon-Leon:1704821121381-23 


CREATE TABLE
    api_token (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
        rol_id UUID REFERENCES rol (id) NOT NULL,
        token TEXT NOT NULL,
        state BOOLEAN NOT NULL DEFAULT TRUE,
        created_date TIMESTAMP NOT NULL DEFAULT NOW (),
        updated_date TIMESTAMP NOT NULL DEFAULT NOW ()
    );


--ROLLBACK DROP TABLE IF EXISTS "api_token";