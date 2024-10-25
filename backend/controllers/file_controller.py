from flask import request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from models.file_model import files_collection
import os
import logging
from bson.objectid import ObjectId
from config.config import UPLOAD_FOLDER
from datetime import datetime

def upload_file():
    try:
        if 'files' not in request.files:
            logging.error('No files part in the request')
            return jsonify(message='No file part'), 400
        
        files = request.files.getlist('files')

        if len(files) == 0:
            loggig.error('No files selected')
            return jsonify(message='No files selected'), 400

        upload_results = []

        for file in files:
            if file.filename == '':
                logging.error('Files with no filename selected')
                return jsonify(message="No selected file"), 400
            
            # Save the file to the server
            file_path = os.path.abspath(os.path.join(UPLOAD_FOLDER, file.filename))
            file.save(file_path)

            owner_name = request.form['owner_name']
            label_name = request.form['label_name']
            file_type = request.form['file_type']
            data_generator = request.form['data_generator']
            chemistry = request.form['chemistry']
            file_date = request.form['upload_date']
            description = request.form['description']
            filename = secure_filename(file.filename)

            # Convert upload_date to a datetime object
            try:
                upload_date = datetime.strptime(file_date, '%Y-%m-%d')  # Convert to datetime
            except ValueError:
                return jsonify(message='Invalid date format. Use YYYY-MM-DD'), 400

            # Collect metadata
            file_data = {
                'file_name' : filename,
                'owner_name':owner_name,
                'label_name' : label_name,
                'file_type': file_type,
                'data_generator' : data_generator,
                'chemistry' : chemistry,
                'upload_date': upload_date,
                'file_path': file_path,
                'description' : description,
                'file_size' : os.path.getsize(file_path) ##
            }

            try:
                files_collection.insert_one(file_data)
                upload_results.append(f'{filename} uploaded successfully')
            except Exception as e:
                logging.error(f'Error inserting file data for {filename}: {str(e)}')
                return jsonify(message=f'Error inserting file data for {filename} into the database'), 500
        
        return jsonify(message='Files uploaded successfully', results=upload_results), 201
    
    except Exception as e:
        logging.error(f'Exception occured during file upload: {str(e)}')
        return jsonify(message=f'An error occured: {str(e)}')

def search_files():
    owner_name = request.args.get('owner_name')
    label_name = request.args.get('label_name')
    file_type = request.args.get('file_type')
    data_generator = request.args.get('data_generator')
    chemistry = request.args.get('chemistry')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Construct query
    query = {}
    if owner_name:
        query['owner_name'] = owner_name
    if label_name:
        query['label_name'] = label_name
    if file_type:
        query['file_type'] = file_type
    if data_generator:
        query['data_generator'] = data_generator
    if chemistry:
        query['chemistry'] = chemistry

    if start_date and end_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            query['upload_date'] = {'$gte': start_date, '$lte': end_date}
        except ValueError:
            return jsonify(message="Invalid date format. Use 'YYYY-MM-DD'"), 400

    try:
        files = files_collection.find(query)
        results = [
            {
                'id': str(file['_id']),
                'filename': file['file_name'],
                'owner_name': file['owner_name'],
                'label_name' : file['label_name'],
                'file_type': file['file_type'],
                'data_generator': file['data_generator'],
                'chemistry': file['chemistry'],
                'upload_date': file['upload_date'].strftime('%Y-%m-%d'),  # Format date for readability
                'description': file['description'],
                'file_size': file['file_size'],
            }
            for file in files
        ]
        return jsonify(results), 200
    except Exception as e:
        logging.error(f'Error searching for files: {str(e)}')
        return jsonify(message='Error searching for files'), 500


def download_file(file_id):
    logging.info(f"Attempting to download file with ID: {file_id}")
    try:
        if not ObjectId.is_valid(file_id):
            logging.warning("Invalid file ID format.")
            return jsonify(message="Invalid file ID"), 400

        file_data = files_collection.find_one({'_id': ObjectId(file_id)})
        if not file_data:
            logging.warning(f"File not found for ID: {file_id}")
            return jsonify(message='File not found'), 404

        logging.info(f"File found: {file_data['file_path']}")
        
        file_path = file_data['file_path']
        return send_from_directory(os.path.dirname(file_path),
                os.path.basename(file_path),
                as_attachment=True
        )

    except Exception as e:
        logging.error(f"Error downloading file: {str(e)}")
        return jsonify(message=f'Error downloading file: {str(e)}'), 500
