--RUN 
--NAME=Marlon Andres Leon Leon
--DESCRIPTION=Crea un permiso para la empresa creada
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

--FIN RUN
--ROLLBACK
DELETE FROM currency
WHERE
    code = 'COP';

--FIN ROLLBACK