import subprocess
import logging
import os

# Path to MongoDB config file
MONGOD_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config/mongod.conf')

def check_and_start_mongodb():
    try:
        output = subprocess.check_output(["pgrep", "-f", "mongod"], stderr=subprocess.STDOUT)
        if output:
            logging.info("MongoDB is running.")
            return None
    except subprocess.CalledProcessError:
        logging.error("MongoDB is not running. Attempting to start it...")

    try:
        mongo_process = subprocess.Popen(["mongod", "--config", MONGOD_CONFIG_PATH])
        logging.info("MongoDB started with config file: %s", MONGOD_CONFIG_PATH)
        return mongo_process
    except Exception as e:
        logging.error("Failed to start MongoDB: %s", str(e))
        return None

def stop_mongodb(process):
    if process:
        process.terminate()
        process.wait()

