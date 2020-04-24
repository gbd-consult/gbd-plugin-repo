FROM python:3

MAINTAINER Tristan Kessler "kessler@gbd-consult.de"

COPY requirements.txt /
RUN pip3 install -r /requirements.txt

COPY ./repo /app/repo

WORKDIR /app

EXPOSE 5000/tcp

CMD ["gunicorn", "-b 0.0.0.0:5000", "repo:app"]
