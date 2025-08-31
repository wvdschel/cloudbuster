FROM docker.io/debian:latest

RUN apt-get update -yy && apt-get install -yy python3-pip chromium chromium-driver python3-venv
ENV PYTHONUNBUFFERED=1

RUN mkdir app
COPY requirements.txt /app/requirements.txt
WORKDIR /app

RUN python3 -m venv /app/venv
RUN /app/venv/bin/pip install -r requirements.txt

COPY . /app
CMD ["/app/venv/bin/python3", "main.py"]