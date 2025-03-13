-- liquibase formatted sql
-- changeset Marlon-Leon:1704821121381-10 insert data currency table

INSERT INTO
    currency (
        id,
        name,
        code,
        symbol,
        state,
        created_date,
        updated_date
    )
VALUES
    (
        uuid_generate_v4 (),
        'Peso Colombiano',
        'COP',
        '$',
        TRUE,
        NOW (),
        NOW ()
    );


--ROLLBACK DELETE FROM currency WHERE code = 'COP';

