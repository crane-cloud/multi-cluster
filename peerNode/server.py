from jsonrpcserver import Success, method, serve, InvalidParams, Result, Error
from datetime import datetime
import sqlite3
from sqlite3 import Error
import re
import json
import os
import time
import socket
#from discovery import check_cluster_info (To be implemented for fast lookups)
from util import create_db_connection, getCPU, getMemory, getDisk
import init, client

@method
def get_availability() -> Result:
    result = {"data": "Cluster on", "message": "success", "status": 200}

    return Success(result)

@method
def get_cluster_resources() -> Result:
    cpu = getCPU()
    memory = getMemory()
    disk = getDisk()

    resources = {"cpu":cpu, "memory":memory, "disk":disk}

    if resources:
        result = {"data": resources, "message": "success", "status": 200}
    else:
        result = {"data": Error, "message": "failed", "status": 500}

    return Success(result)

hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
port = int(os.getenv('PORT'))

if __name__ == "__main__":
    init.main()
    serve(ip_address, port)
    time.sleep(120)
    client.main()