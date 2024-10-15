from flask import Flask
from flask_cors import CORS
#from config.config import UPLOAD_FOLDER
from routes.file_routes import file_bp
import os

app = Flask(__name__)
CORS(app)

# Ensure upload directory exists
#if not os.path.exists(UPLOAD_FOLDER):
#    os.makedirs(UPLOAD_FOLDER)


app.register_blueprint(file_bp, url_prefix='/api/files')

if __name__ == '__main__':
    app.run(debug=True, port=5000)


