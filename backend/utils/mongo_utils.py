import subprocess
import logging
import os


# Calculate the base path dynamically
BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Calculate the mongod.conf path dynamically
def get_mongod_conf_path():
    # Assuming 'config' is the folder containing mongod.conf
    config_path = os.path.join(BASE_PATH, 'backend', 'config', 'mongod.conf')
    return config_path


# Update mongod.conf with the dynamically calculated paths
def update_mongod_config():
    # Get the dynamic path for the config
    MONGOD_CONFIG_PATH = get_mongod_conf_path()

    # Paths to the data and log directories (dynamically calculated)
    DATA_PATH = os.path.join(BASE_PATH, 'data')
    LOG_PATH = os.path.join(BASE_PATH, 'logs')

    os.makedirs(DATA_PATH, exist_ok=True)
    os.makedirs(LOG_PATH, exist_ok=True)
    
    try:
        # Read the original configuration file
        with open(MONGOD_CONFIG_PATH, 'r') as file:
            config_data = file.read()

        # Replace the dbPath and log path with dynamic values
        config_data = config_data.replace("../data", DATA_PATH)
        config_data = config_data.replace("../logs", LOG_PATH)

        # Write the updated config data back to the file
        with open(MONGOD_CONFIG_PATH, 'w') as file:
            file.write(config_data)

        logging.info("Updated mongod.conf with dynamic paths.")
    except Exception as e:
        logging.error("Failed to update mongod.conf: %s", str(e))


def check_and_start_mongodb():
    # Get the dynamic path for the config file
    MONGOD_CONFIG_PATH = get_mongod_conf_path()

    # Update the mongod.conf file before starting MongoDB
    update_mongod_config()
    
    try:
        # Check if MongoDB is already running
        output = subprocess.check_output(["pgrep", "-f", "mongod"], stderr=subprocess.STDOUT)
        if output:
            logging.info("MongoDB is already running. Directing to config file: %s", MONGOD_CONFIG_PATH)
            # If MongoDB is running, just use the config path
            subprocess.Popen(["mongod", "--config", MONGOD_CONFIG_PATH])
            return None  # We don't need to restart it, just direct to the config
    except subprocess.CalledProcessError:
        # MongoDB is not running, so we proceed to start it
        logging.error("MongoDB is not running. Attempting to start it with config: %s", MONGOD_CONFIG_PATH)


        try:
            # Start MongoDB with the updated config file path
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
