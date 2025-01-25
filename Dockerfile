FROM python:3.12

RUN apt-get update

WORKDIR /app

RUN pip install --no-cache-dir flask psycopg2 python-dotenv bcrypt flask-jwt-extended

COPY . .
