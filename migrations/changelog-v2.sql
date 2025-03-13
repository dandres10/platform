-- liquibase formatted sql
-- changeset Marlon-Leon:1704821121381-2 insert data language table

INSERT INTO
    language (
        id,
        name,
        code,
        native_name,
        state,
        created_date,
        updated_date
    )
VALUES
    (
        uuid_generate_v4 (),
        'Spanish',
        'es',
        'Español',
        TRUE,
        NOW (),
        NOW ()
    );
 
INSERT INTO
    language (
        id,
        name,
        code,
        native_name,
        state,
        created_date,
        updated_date
    )
VALUES
    (
        uuid_generate_v4 (),
        'English',
        'en',
        'Ingles',
        TRUE,
        NOW (),
        NOW ()
    );


--ROLLBACK DELETE FROM language WHERE code = 'es'; 
--ROLLBACK DELETE FROM language WHERE code = 'en';


