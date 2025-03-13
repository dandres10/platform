-- liquibase formatted sql
-- changeset Marlon-Leon:1704821121381-1 create_base_tables

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE
    language (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
        name VARCHAR(100) NOT NULL,
        code VARCHAR(10) UNIQUE NOT NULL,
        native_name VARCHAR(100),
        state BOOLEAN NOT NULL DEFAULT TRUE,
        created_date TIMESTAMP NOT NULL DEFAULT NOW (),
        updated_date TIMESTAMP NOT NULL DEFAULT NOW ()
    );


 
CREATE TABLE
    currency (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
        name VARCHAR(255) NOT NULL,
        code VARCHAR(10) UNIQUE NOT NULL,
        symbol VARCHAR(10) NOT NULL,
        state BOOLEAN NOT NULL DEFAULT TRUE,
        created_date TIMESTAMP NOT NULL DEFAULT NOW (),
        updated_date TIMESTAMP NOT NULL DEFAULT NOW ()
    );


 
CREATE TABLE
    country (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
        name VARCHAR(255) NOT NULL,
        code VARCHAR(10) UNIQUE NOT NULL,
        phone_code VARCHAR(10) NOT NULL,
        state BOOLEAN NOT NULL DEFAULT TRUE,
        created_date TIMESTAMP NOT NULL DEFAULT NOW (),
        updated_date TIMESTAMP NOT NULL DEFAULT NOW ()
    );


 
CREATE TABLE
    company (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
        name VARCHAR(255) NOT NULL,
        inactivity_time INT NOT NULL DEFAULT 20,
        nit VARCHAR(255) UNIQUE NOT NULL,
        state BOOLEAN NOT NULL DEFAULT TRUE,
        created_date TIMESTAMP NOT NULL DEFAULT NOW (),
        updated_date TIMESTAMP NOT NULL DEFAULT NOW ()
    );



 
CREATE TABLE
    location (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
        company_id UUID REFERENCES company (id),
        country_id UUID REFERENCES country (id),
        name VARCHAR(255) NOT NULL,
        address text NOT NULL,
        city VARCHAR(100) NOT NULL,
        phone VARCHAR(20) NOT NULL,
        email VARCHAR(100) NOT NULL,
        main_location BOOLEAN NOT NULL DEFAULT False,
        state BOOLEAN NOT NULL DEFAULT TRUE,
        created_date TIMESTAMP NOT NULL DEFAULT NOW (),
        updated_date TIMESTAMP NOT NULL DEFAULT NOW ()
    );


 
CREATE TABLE
    currency_location (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
        currency_id UUID REFERENCES "currency" (id) NOT NULL,
        location_id UUID REFERENCES location (id) NOT NULL,
        state BOOLEAN NOT NULL DEFAULT TRUE,
        created_date TIMESTAMP NOT NULL DEFAULT NOW (),
        updated_date TIMESTAMP NOT NULL DEFAULT NOW (),
        UNIQUE (currency_id, location_id)
    );


 
CREATE TABLE
    platform (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
        language_id UUID REFERENCES language (id) NOT NULL,
        location_id UUID REFERENCES location (id) NOT NULL,
        currency_id UUID REFERENCES "currency" (id) NOT NULL,
        token_expiration_minutes INT NOT NULL DEFAULT 60,
        refresh_token_expiration_minutes INT NOT NULL DEFAULT 62,
        created_date TIMESTAMP NOT NULL DEFAULT NOW (),
        updated_date TIMESTAMP NOT NULL DEFAULT NOW ()
    );


 
CREATE TABLE
    menu (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
        company_id UUID REFERENCES company (id) NOT NULL,
        "name" varchar(100) NOT NULL,
        label varchar(300) NOT NULL,
        description varchar(300) NOT NULL,
        top_id UUID NOT NULL,
        route varchar(300) NOT NULL,
        state BOOLEAN NOT NULL DEFAULT TRUE,
        icon varchar(50) NOT NULL,
        created_date TIMESTAMP NOT NULL DEFAULT NOW (),
        updated_date TIMESTAMP NOT NULL DEFAULT NOW ()
    );


 
CREATE TABLE
    rol (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
        company_id UUID REFERENCES company (id) NULL,
        name VARCHAR(255) NOT NULL,
        code VARCHAR(255) NOT NULL,
        description TEXT,
        state BOOLEAN NOT NULL DEFAULT TRUE,
        created_date TIMESTAMP NOT NULL DEFAULT NOW (),
        updated_date TIMESTAMP NOT NULL DEFAULT NOW (),
        UNIQUE (company_id, code)
    );


 
CREATE TABLE
    permission (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
        company_id UUID REFERENCES company (id) NULL,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        state BOOLEAN NOT NULL DEFAULT TRUE,
        created_date TIMESTAMP NOT NULL DEFAULT NOW (),
        updated_date TIMESTAMP NOT NULL DEFAULT NOW ()
    );


 
CREATE TABLE
    rol_permission (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
        rol_id UUID REFERENCES "rol" (id) NOT NULL,
        permission_id UUID REFERENCES "permission" (id) NOT NULL,
        state BOOLEAN NOT NULL DEFAULT TRUE,
        created_date TIMESTAMP NOT NULL DEFAULT NOW (),
        updated_date TIMESTAMP NOT NULL DEFAULT NOW (),
        UNIQUE (rol_id, permission_id)
    );
 

 
CREATE TABLE
    menu_permission (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
        menu_id UUID REFERENCES "menu" (id) NOT NULL,
        permission_id UUID REFERENCES "permission" (id) NOT NULL,
        state BOOLEAN NOT NULL DEFAULT TRUE,
        created_date TIMESTAMP NOT NULL DEFAULT NOW (),
        updated_date TIMESTAMP NOT NULL DEFAULT NOW (),
        UNIQUE (menu_id, permission_id)
    );


 
CREATE TABLE
    "user" (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
        platform_id UUID REFERENCES platform (id) NOT NULL,
        password VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        first_name VARCHAR(255),
        last_name VARCHAR(255),
        phone VARCHAR(20),
        refresh_token text,
        state BOOLEAN NOT NULL DEFAULT TRUE,
        created_date TIMESTAMP NOT NULL DEFAULT NOW (),
        updated_date TIMESTAMP NOT NULL DEFAULT NOW ()
    );


 
CREATE TABLE
    user_location_rol (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
        user_id UUID REFERENCES "user" (id) NOT NULL,
        location_id UUID REFERENCES location (id) NOT NULL,
        rol_id UUID REFERENCES rol (id) NOT NULL,
        state BOOLEAN NOT NULL DEFAULT TRUE,
        created_date TIMESTAMP NOT NULL DEFAULT NOW (),
        updated_date TIMESTAMP NOT NULL DEFAULT NOW (),
        UNIQUE (user_id, location_id, rol_id)
    );


 
CREATE TABLE
    translation (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4 (),
        key VARCHAR(255) NOT NULL,
        language_code VARCHAR(10) NOT NULL REFERENCES language (code),
        translation TEXT NOT NULL,
        context VARCHAR(255),
        state BOOLEAN NOT NULL DEFAULT TRUE,
        created_date TIMESTAMP NOT NULL DEFAULT NOW (),
        updated_date TIMESTAMP NOT NULL DEFAULT NOW (),
        UNIQUE (key, language_code, context)
    );



 

--ROLLBACK DROP TABLE IF EXISTS "translation";
--ROLLBACK DROP TABLE IF EXISTS user_location_rol; 
--ROLLBACK DROP TABLE IF EXISTS "user";
--ROLLBACK DROP TABLE IF EXISTS menu_permission; 
--ROLLBACK DROP TABLE IF EXISTS rol_permission;
--ROLLBACK DROP TABLE IF EXISTS "permission";
--ROLLBACK DROP TABLE IF EXISTS rol;
--ROLLBACK DROP TABLE IF EXISTS menu;
--ROLLBACK DROP TABLE IF EXISTS platform;
--ROLLBACK DROP TABLE IF EXISTS currency_location;
--ROLLBACK DROP TABLE IF EXISTS "location";
--ROLLBACK DROP TABLE IF EXISTS company;
--ROLLBACK DROP TABLE IF EXISTS country;
--ROLLBACK DROP TABLE IF EXISTS currency;
--ROLLBACK DROP TABLE IF EXISTS "language";