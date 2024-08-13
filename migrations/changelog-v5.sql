--RUN 
--NAME=Marlon Andres Leon Leon
--DESCRIPTION=Crea un pais

INSERT INTO country (
    id, 
    name, 
    code, 
    phone_code, 
    state, 
    created_date, 
    updated_date
)
VALUES (
    uuid_generate_v4(),   -- Genera un UUID automáticamente para la columna id
    'Colombia',           -- Nombre del país
    'CO',                 -- Código ISO del país
    '+57',                -- Código telefónico del país
    TRUE,                 -- Estado (activo)
    NOW(),                -- Fecha de creación
    NOW()                 -- Fecha de actualización
);



--FIN RUN

--ROLLBACK
DELETE FROM country WHERE code = 'CO';
--FIN ROLLBACK
