import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from backend.config.config import get_config

# Load config settings
CONFIG = get_config()

# Set up log file naming and directory structure
LOG_FILE = f"{datetime.now().strftime('%y_%m_%d_%H_%M_%S')}.log"
logs_path = CONFIG['LOG_DIR']
os.makedirs(logs_path, exist_ok=True)

LOG_FILE_PATH = os.path.join(logs_path, LOG_FILE)
LOG_FORMAT = "[ %(asctime)s] %(lineno)d %(name)s - %(levelname)s - %(module)s - %(message)s"

# Create a rotating file handler with a 10MB max file size and 5 backups
rotating_handler = RotatingFileHandler(LOG_FILE_PATH, maxBytes=10*1024*1024, backupCount=5)
rotating_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# Configure logging to write to both file and console
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        rotating_handler,
        logging.StreamHandler(sys.stdout)
    ]
)


# Main execution (used when running standalone or for application setup)
if __name__ == "__main__":
    logging.info("Logging has started.")

