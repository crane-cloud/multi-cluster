FROM python:3.8-slim-buster

RUN apt update
RUN apt install -y iperf3

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . /app

EXPOSE 5100

# CMD [ "python", "starter.py", "-v"]
