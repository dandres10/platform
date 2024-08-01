#correr el aplicativo 

1. source env/bin/activate
2. uvicorn infrastructure.web.main:app --reload

ENV=qa uvicorn src.infrastructure.web.main:app --reload
ENV=production src.uvicorn infrastructure.web.main:app --reload

pip install -r pipfiles.txt 
