FROM python:3.11.9 AS build

WORKDIR /app
COPY . /app

RUN pip install -r pipfiles.txt --root-user-action=ignore

EXPOSE 8000

ENV ENV=prod

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
