FROM python:2.7-alpine

RUN apk update
RUN apk add python python-dev py-virtualenv postgresql-dev libjpeg-dev

WORKDIR /app

ADD . .

RUN ls