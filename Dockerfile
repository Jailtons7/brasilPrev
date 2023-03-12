FROM python:3.10.6

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update &&\
    apt install curl -y

RUN mkdir /app
COPY requirements.txt /app/.
WORKDIR /app
RUN apt update && apt install -y vim
RUN pip install --upgrade pip
RUN pip install --upgrade -r requirements.txt
