# syntax=docker/dockerfile:1
FROM python:3

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

# install python dependencies
COPY requirements.txt /code/requirements.txt
RUN pip install -r /code/requirements.txt