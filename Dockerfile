FROM python:3.8.3-slim


COPY requirements.txt /
RUN pip3 install -r /requirements.txt

COPY ./repo /app/repo

WORKDIR /app


CMD ["gunicorn", "-b 0.0.0.0:4567", "repo:app"]
