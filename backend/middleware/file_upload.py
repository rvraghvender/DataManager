from flask import request, jsonify
from werkzeug.utils import secure_filename
import os
from config.config import UPLOAD_FOLDER
from models.file_model import files_collection

def upload_file_handler():
    if 'file' not in request.files:
        return jsonify(message='No file part'), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify(message='No selected file'), 400
    
    owner_name = request.form['owner_name']
    file_type = request.form['file_type']
    file_date = request.form['upload_date']
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    file.save(file_path)
    
    file_data = {
        'owner_name': owner_name,
        'file_type': file_type,
        'upload_date': file_date,
        'file_path': file_path
    }
    
    files_collection.insert_one(file_data)
    return {'message': 'File uploaded successfully', 'file': file_data}

