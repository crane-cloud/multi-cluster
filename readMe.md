## MULTI-CLUSTER MONITOR APP

- A python app to monitor(scrape and store) metrics about clusters in a multi-cluster setup.


## TO SETUP

1. Clone this repository `git clone https://github.com/crane-cloud/multi-cluster.git`
2. Create a virtual environment 

    - App was developed with `Python 3.6`.

    - Make sure you have `pip` installed on your machine.

    - Create a pip virtual environment you can call it `venv`

    - Activate the virtual environment: `. venv/bin/activate`

3. Install required dependencies from requirements.txt file `pip install -r requirements.txt`
4. Run server  `python server.py`
5. Run client  `python client.py`
