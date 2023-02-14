FROM python:3.9.7-slim-buster

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

COPY kanoe/ kanoe/
COPY database/ database/

ENTRYPOINT ["flask", "--app", "kanoe", "--debug", "run", "-h", "0.0.0.0"]
