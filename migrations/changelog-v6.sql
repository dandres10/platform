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
    '83950f65-ae93-4214-b5b1-8ccd479180b3',  -- UUID de la compañía a la que pertenece la ubicación (debe existir en la tabla company)
    'e09995a8-4bd7-4bd1-8fbe-4adbd8586cfd',  -- UUID del país (debe existir en la tabla country)
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
