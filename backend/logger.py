import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from backend.config.config import get_config

CONFIG = get_config()

LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
logs_path = CONFIG['LOG_DIR']
os.makedirs(logs_path, exist_ok=True)

LOG_FILE_PATH = os.path.join(logs_path, LOG_FILE)

logging.basicConfig(
    # filename=LOG_FILE_PATH,
    format="[ %(asctime)s] %(lineno)d %(name)s - %(levelname)s - %(module)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler(LOG_FILE_PATH),
        logging.StreamHandler(sys.stdout)
    ]
)

############################################################
'''                       Additional things              '''

# Create a rotating file handler
""" 10 MB max size, keep 5 backup copies """ 
# rotating_handler = RotatingFileHandler(LOG_FILE_PATH, maxBytes=10*1024*1024, backupCount=5)  
# rotating_handler.setFormatter(logging.Formatter("[ %(asctime)s] %(lineno)d %(name)s - %(levelname)s - %(message)s"))
# logging.getLogger().addHandler(rotating_handler)


if __name__ == "__main__":
    logging.info("Loggin has started.")
