FROM python:3.11.9 as build


WORKDIR /app
COPY . /app

RUN pip install -r pipfiles.txt --root-user-action=ignore

EXPOSE 8000

ENV ENV=qa


CMD ["uvicorn", "src.infrastructure.web.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
