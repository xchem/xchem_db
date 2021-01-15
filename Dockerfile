# base image
FROM python:3.6-slim

# environment for python logging
# send output to terminal without buffer
ENV PYTHONBUFFERED 1

RUN mkdir /xcdb
WORKDIR /xcdb
ADD . /xcdb
RUN chmod -R 777 /xcdb

# install needed packages
RUN apt-get update \
    && apt-get install -y python-psycopg2 graphviz libgraphviz-dev \
    && apt-get install -y default-libmysqlclient-dev build-essential \
    && pip install --trusted-host pypi.python.org -r requirements.txt \
    && apt-get remove -y default-libmysqlclient-dev build-essential
