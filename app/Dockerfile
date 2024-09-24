FROM python:3.11.9-slim-bullseye

RUN apt update
RUN apt install -y netcat

WORKDIR /app

RUN pip install -U pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /content/static

ENTRYPOINT [ "/app/entrypoint.sh" ]
