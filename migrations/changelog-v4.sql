--RUN 
--NAME=Marlon Andres Leon Leon
--DESCRIPTION=Crea una empresa

INSERT INTO company (id, name, inactivity_time, nit, state, created_date, updated_date)
VALUES (
    uuid_generate_v4(),         
    'Company #1',          
    30,                         
    '123456789',                
    TRUE,                       
    NOW(),                      
    NOW()                       
);



--FIN RUN

--ROLLBACK
DELETE FROM company WHERE nit = '123456789';
--FIN ROLLBACK
