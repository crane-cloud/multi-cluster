from jsonrpcserver import Success, method, serve, InvalidParams, Result, Error
from datetime import datetime
import sqlite3
from sqlite3 import Error
import re
import json
import os
from discovery import check_cluster_info
from metrics import getCPU, getMemory, getDisk
from util import create_db_connection

@method
def get_availability() -> Result:
    result = {"data": "Cluster on", "message": "success", "status": 200}

    return Success(result)

@method
def get_server_resources() -> Result:
    cpu = getCPU()
    memory = getMemory()
    disk = getDisk()

    resources = {"cpu":cpu, "memory": memory, "disk":disk}

    if resources:
        result = {"data": resources, "message": "success", "status": 201}
    else:
        result = {"data": Error, "message": "failed", "status": 500}

    return Success(result)
