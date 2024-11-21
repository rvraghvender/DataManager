import subprocess
from backend.logger import logging
import os
from backend.config.config import get_config

# Calculate the mongod.conf path dynamically
def get_mongod_conf_path():
    CONFIG = get_config()
    # Assuming 'config' is the folder containing mongod.conf
    config_path = os.path.join(CONFIG['ROOT_DIR'], 'backend', 'config', 'mongod.conf')
    return config_path


# Update mongod.conf with the dynamically calculated paths
def update_mongod_config():
    # Get the dynamic path for the config
    MONGOD_CONFIG_PATH = get_mongod_conf_path()
    CONFIG = get_config()    
    try:
        # Read the original configuration file
        with open(MONGOD_CONFIG_PATH, 'r') as file:
            config_data = file.readlines()

        # Flag to check if dbPath and log paths were found and updated
        dbPath_updated = False
        logPath_updated = False

        # Iterate over lines and update dbPath and systemLog.path
        for i, line in enumerate(config_data):
            # Check for dbPath and update if found
            if "dbPath" in line:
                config_data[i] = f"    dbPath: {CONFIG['MONGO_DATA_DIR']}\n"
                dbPath_updated = True
            # Check for systemLog.path and update if found
            elif "path" in line and "systemLog" in config_data[i-2]:
                config_data[i] = f"    path: {CONFIG['MONGO_LOG_DIR']}/mongod.log\n"
                logPath_updated = True

        # If dbPath or logPath were not found, append them to the file
        if not dbPath_updated:
            config_data.append(f"storage:\n    dbPath: {CONFIG['MONGO_DATA_DIR']}\n")
        if not logPath_updated:
            config_data.append(f"systemLog:\n    destination: file\n    path: {CONFIG['MONGO_LOG_DIR']}/mongod.log\n    logAppend: true\n")

        # Write the updated config data back to the file
        with open(MONGOD_CONFIG_PATH, 'w') as file:
            file.writelines(config_data)

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
