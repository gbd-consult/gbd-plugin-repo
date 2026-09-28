FROM python:3.14.2-slim


COPY requirements.txt /
RUN pip3 install -r /requirements.txt

COPY ./repo /app/repo

WORKDIR /app


CMD ["gunicorn", "--bind", "0.0.0.0:4567", "--timeout", "1800", "--workers", "3", "repo:app"]
