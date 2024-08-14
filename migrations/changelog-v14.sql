--RUN 
--NAME=Marlon Andres Leon Leon
--DESCRIPTION=Crea un permiso para la empresa creada
INSERT INTO
  menu (
    id,
    company_id,
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
    'd5c552fb-9434-4301-83af-03f3ca4195cf', -- company_id
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
  company_id = 'd5c552fb-9434-4301-83af-03f3ca4195cf'
  AND name = 'Home'
  AND route = '/home';

--FIN ROLLBACK