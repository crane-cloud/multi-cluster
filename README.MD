# Multicluster Application

## Create the view network
```bash
docker network create view
```
This enables the containers to communicate with each other.

## Run central server

```bash
cd viewServer
```
Start the server:
```bash
make start
```

## Run the Peer application

```bash
cd peerNode
```
Start the peer node
```bash
make start
```

This will start and initialize a peer node as defined in the docker-compose file.

## To start the peer application

SSH into any of the peer node containers
```bash
docker exec -it <container-name> /bin/bash
```
Run the following command
```bash
python server.py
```
This should initialise cluster discovery and setup the cluster.


## To kill the containers and volumes to have a fresh start

```bash
cd peerNode
```
Run the following command
```bash
make clean
```
This will kill all the containers and remove the volumes created by the docker-compose file so that you can begin again with a fresh start.
