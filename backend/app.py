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
from utils.mongo_utils import check_and_start_mongodb, stop_mongodb

logging.basicConfig(level=logging.INFO)



def create_app():
    app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')
    CORS(app)
    
    # Ensure the upload directory exists
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # Register Blueprints
    app.register_blueprint(file_bp, url_prefix='/api/files')

    @app.route('/')
    def index():
       return render_template('index.html')
    
   return app


def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Start MongoDB if not running
    mongo_process = check_and_start_mongodb()
    
    app = create_app()
    try:
        app.run(debug=True, port=5000)
    except KeyboardInterrupt:
        logging.info("Shutting down MongoDB...")
        stop_mongodb(mongo_process)
        logging.info("MongoDB shut down successfully.")

if __name__ == '__main__':
    main()

