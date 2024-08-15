--RUN 
--NAME=Marlon Andres Leon Leon
--DESCRIPTION=Crea un permiso para la empresa creada
INSERT INTO
  menu (
    id,
    company_id,
    label,
    name,
    description,
    top_id,
    route,
    state,
    icon,
    created_date,
    updated_date
  )
VALUES
  (
    uuid_generate_v4 (),
    '83950f65-ae93-4214-b5b1-8ccd479180b3', -- company_id
    'Encuentra todo aca',
    'Home', -- name
    'Home for the application', -- description
    NULL, -- top_id
    '/home', -- route
    TRUE, -- state
    'home-icon', -- icon
    NOW (), -- created_date
    NOW () -- updated_date
  );

--FIN RUN
--ROLLBACK
DELETE FROM menu
WHERE
  company_id = '83950f65-ae93-4214-b5b1-8ccd479180b3'
  AND name = 'Home'
  AND route = '/home';

--FIN ROLLBACK