FROM videotheque:1.0

RUN apt-get update

WORKDIR /api

RUN pip install --no-cache-dir flask

COPY . .
