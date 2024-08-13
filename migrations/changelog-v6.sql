--RUN 
--NAME=Marlon Andres Leon Leon
--DESCRIPTION=Crea un sede o location de la empresa

INSERT INTO location (
    id, 
    company_id, 
    country_id, 
    name, 
    address, 
    city, 
    phone, 
    email, 
    main_location, 
    state, 
    created_date, 
    updated_date
)
VALUES (
    uuid_generate_v4(),                  -- Genera un UUID automáticamente para la columna id
    'd5c552fb-9434-4301-83af-03f3ca4195cf',  -- UUID de la compañía a la que pertenece la ubicación (debe existir en la tabla company)
    'ba14bca3-1eb2-4cc6-9389-4e9597d0111f',  -- UUID del país (debe existir en la tabla country)
    'Zona G',                        -- Nombre de la ubicación
    '1234 Elm Street',                    -- Dirección
    'Bogota',                         -- Ciudad
    '4562323',                        -- Teléfono
    'info@company.com',                   -- Correo electrónico
    TRUE,                                 -- Indica si es la ubicación principal
    TRUE,                                 -- Estado (activo)
    NOW(),                                -- Fecha de creación
    NOW()                                 -- Fecha de actualización
);

--FIN RUN

--ROLLBACK
DELETE FROM location WHERE name = 'Zona G' AND address = '1234 Elm Street';
--FIN ROLLBACK
