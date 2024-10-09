-- liquibase formatted sql
-- changeset Marlon-Leon:1704821121381-19 insert data rol table
INSERT INTO
    rol (
        id,
        company_id,
        "name",
        code,
        description,
        state,
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
                company
            LIMIT
                1
        ),
        'user',
        'USER',
        'core_rol_user',
        true,
        now (),
        now ()
    );

--ROLLBACK DELETE FROM rol WHERE code = 'USER';