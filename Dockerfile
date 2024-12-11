FROM python:3.12

RUN apt-get update

WORKDIR /app

RUN pip install --no-cache-dir flask

COPY . .
