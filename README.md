#correr el aplicativo 

1. source env/bin/activate
2. uvicorn infrastructure.web.main:app --reload

ENV=qa uvicorn main:app --reload
ENV=production uvicorn main:app --reload

pip install -r pipfiles.txt 
