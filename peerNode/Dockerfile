FROM python:3.9-slim-buster

RUN apt update
RUN apt install -y python3-dev

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . /app

CMD [ "python3", "server.py", "-v"]