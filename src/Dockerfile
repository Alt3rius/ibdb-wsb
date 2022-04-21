FROM python:3.8-buster

RUN pip install flask flask-migrate flask-sqlalchemy requests psycopg2-binary gunicorn

COPY ./ibdb /var/www/ibdb

WORKDIR /var/www/ibdb

ENTRYPOINT gunicorn --bind 0.0.0.0 wsgi:app