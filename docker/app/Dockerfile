FROM ubuntu:14.04 
# python:2.7-alpine

# RUN apk update
# RUN apk add git make gcc python python-dev py-virtualenv postgresql-dev jpeg libxml2 binutils curl

RUN apt-get update
RUN apt-get install -y curl python-dev python-virtualenv postgresql-server-dev-9.3 libgeos-3.4.2 libgdal1h libjpeg-dev libxml2-dev python-psycopg2 binutils libproj-dev gdal-bin postgis postgresql-9.3-postgis-2.1

WORKDIR /app

COPY Makefile /app

COPY . /app

RUN git clone https://github.com/CIRB/mobileserverstatus.git mobileserverstatus

RUN make develop