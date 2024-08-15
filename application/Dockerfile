FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN mkdir /application

COPY requirements.txt /application/requirements.txt
COPY alembic.ini /application/alembic.ini
COPY alembic /application/alembic

WORKDIR /application

ADD . /application

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /application/requirements.txt

EXPOSE 8000
