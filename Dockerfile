FROM python:3.11.4-slim-buster

RUN apt-get update -q && \
    apt-get install -q -y \
        libglib2.0-0 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

COPY requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

COPY paddle/ paddle/
COPY database/ database/

ENTRYPOINT ["flask", "--app", "paddle", "--debug", "run", "-h", "0.0.0.0"]
