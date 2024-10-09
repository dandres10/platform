-- liquibase formatted sql
-- changeset Marlon-Leon:1704821121381-21 insert data rol table


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
        (
            SELECT
                id
            FROM
                "language"
            LIMIT
                1
        ),
        (
            SELECT
                id
            FROM
                "location"
            LIMIT
                1
        ),
        (
            SELECT
                id
            FROM
                "currency"
            LIMIT
                1
        ),
        60,
        62,
        NOW (),
        NOW ()
    );

INSERT INTO
    "user" (
        platform_id,
        password,
        email,
        first_name,
        last_name,
        phone,
        refresh_token,
        created_date,
        updated_date
    )
VALUES
    (
        (
            SELECT
                id
            FROM
                platform
            ORDER BY
                created_date DESC
            LIMIT
                1
        ),
        '$2b$12$.BsJdi.jmp2AivooGAn7FOEazabWXg/mP04ciMEr8MUh3J9f4jKNm',
        'colaborador@goluti.com',
        'colaborador',
        'Leon',
        '234567890',
        NULL,
        NOW (),
        NOW ()
    );


INSERT INTO
  user_location_rol (
    id,
    user_id,
    rol_id,
    location_id,
    state,
    created_date,
    updated_date
  )
VALUES
  (
    uuid_generate_v4 (),
    (SELECT id FROM "user" WHERE email = 'colaborador@goluti.com' LIMIT 1), 
    (SELECT id FROM "rol" WHERE code = 'COLLA' LIMIT 1), 
    (SELECT id FROM "location" LIMIT 1), 
    TRUE,
    NOW (),
    NOW ()
  );


--ROLLBACK DELETE FROM rol WHERE code = 'USER';