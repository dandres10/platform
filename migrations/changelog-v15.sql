-- liquibase formatted sql
-- changeset Marlon-Leon:1704821121381-15 insert data menu table

WITH generated_uuid AS (
  SELECT uuid_generate_v4() AS id
)
INSERT INTO menu (
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
VALUES (
  (SELECT id FROM generated_uuid),    
  (SELECT id FROM "company" LIMIT 1), 
  'Encuentra todo acá',               
  'Home',                             
  'Home for the application',         
  (SELECT id FROM generated_uuid),    
  '/home',                            
  TRUE,                               
  'home-icon',                        
  NOW(),                              
  NOW()                               
);

--ROLLBACK DELETE FROM menu;

