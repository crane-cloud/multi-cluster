FROM python:3.8-slim-buster

RUN apt update
RUN apt install -y iperf3
RUN apt install -y gcc python3-dev

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . /app

RUN iperf3 -s -D -p 5201 

EXPOSE 5100 5201

# CMD [ "python", "starter.py", "-v"]
