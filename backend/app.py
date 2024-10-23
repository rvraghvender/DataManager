from flask import Flask, render_template
from flask_cors import CORS
from config.config import UPLOAD_FOLDER, MONGO_URI
from routes.file_routes import file_bp
import os
import time
import subprocess
import logging
from routes.file_routes import file_bp
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file
load_dotenv()

# Path to the MongoDB configuration file
MONGOD_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'backend/config/mongod.conf')

# Check if MongoDB is running and start it if not
def check_and_start_mongodb():
    try:
        output = subprocess.check_output(["pgrep", "-f", "mongod"], stderr=subprocess.STDOUT)
        if output:
            logging.info("MongoDB is running.")
            return None
    except subprocess.CalledProcessError:
        logging.error("MongoDB is not running. Attempting to start it...")

    # Start MongoDB with the specified config file
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

app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')

#app = Flask(__name__)
CORS(app)

# Ensure upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/')
def index():
    return render_template('index.html')


app.register_blueprint(file_bp, url_prefix='/api/files')

if __name__ == '__main__':

    # Run the check when the app starts
    mongo_process = check_and_start_mongodb()

    time.sleep(5)
    
    try:
        app.run(debug=True, port=5000)
    except KeyboardInterrupt:
        logging.info("Shutting down MongoDB...")
        stop_mongodb(mongo_process)
        logging.info("MongoDB shut down successfully.")


