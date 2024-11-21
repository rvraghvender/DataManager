from flask import Flask, render_template
from flask_cors import CORS
from backend.config.config import get_config
from backend.routes.file_routes import file_bp
import os
from backend.logger import logging
from dotenv import load_dotenv
from backend.utils.mongo_utils import check_and_start_mongodb, stop_mongodb

def create_app():
    app = Flask(__name__, static_folder='../frontend', template_folder='../frontend')
    CORS(app)

    CONFIG = get_config()
    UPLOAD_FOLDER = CONFIG['UPLOAD_FOLDER']
    
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
        app.run(debug=False, host='0.0.0.0',  port=5000)
    except KeyboardInterrupt:
        logging.info("Shutting down MongoDB...")
        stop_mongodb(mongo_process)
        logging.info("MongoDB shut down successfully.")

if __name__ == '__main__':
    main()

