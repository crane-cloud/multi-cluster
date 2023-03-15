FROM python:3.8-slim-buster

RUN apt update
RUN apt install -y iperf3
RUN apt install -y gcc python3-dev

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . /app

EXPOSE 5001

#CMD [ "python", "server.py", "-v"]