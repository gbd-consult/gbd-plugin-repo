FROM python:3.14.2-slim


COPY requirements.txt /
RUN pip3 install -r /requirements.txt

COPY ./repo /app/repo

WORKDIR /app

COPY ./doc/vendor /app/doc/vendor
COPY ./doc/theme /app/doc/theme
COPY ./doc/books /app/doc/books
COPY ./doc/doc.py ./doc/options.json /app/doc/
RUN python3 doc/doc.py build


CMD ["gunicorn", "--bind", "0.0.0.0:4567", "--timeout", "1800", "--workers", "3", "repo:app"]
