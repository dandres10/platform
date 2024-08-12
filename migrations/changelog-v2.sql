--RUN
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
        'English',
        TRUE,
        NOW (),
        NOW ()
    );

--FIN RUN

--ROLLBACK
DELETE FROM language
WHERE
    code = 'es';

DELETE FROM language
WHERE
    code = 'en';

--FIN ROLLBACK