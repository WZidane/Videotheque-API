FROM python:alpine3.21

WORKDIR /app

RUN pip install Flask

COPY API/ .

CMD ["python", "app.py"]
