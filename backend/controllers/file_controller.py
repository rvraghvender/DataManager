import os
import time
from flask import request, jsonify, send_from_directory, send_file
from werkzeug.utils import secure_filename
from backend.models.file_model import get_files_collection
from io import BytesIO
from backend.utils.utils import verify_file_checksum, calculate_file_checksum
from backend.utils.utils import establish_smb_connection
from backend.utils.utils import create_nas_directories
from backend.utils.utils import upload_to_nas
from backend.config.config import get_config
from backend.logger import logging
from bson.objectid import ObjectId
from backend.config.config import UPLOAD_FOLDER
from datetime import datetime
from dotenv import load_dotenv


def upload_file():
    """
    Handle file uploads and insert metadata into the database.
    """
    try:
        start_time = time.time()

        if 'files' not in request.files:
            logging.error('No files part in the request')
            return jsonify(message='No file part'), 400

        files = request.files.getlist('files')

        if not files:
            logging.error('No files selected')
            return jsonify(message='No files selected'), 400

        upload_results = []

        # Establish the SMB connection once
        conn = establish_smb_connection()

        for file in files:
            if file.filename == '':
                logging.error('Files with no filename selected')
                return jsonify(message="No selected file"), 400
            
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
                upload_date = datetime.strptime(file_date, '%Y-%m-%d')
            except ValueError:
                return jsonify(message='Invalid date format. Use YYYY-MM-DD'), 400

            # Read the file data directly from the uploaded file (in memory)
            file_data = file.read()
            logging.info('File data read.')

            # Upload the file to the NAS and get the NAS path
            try:
                file_checksum, nas_file_path = upload_to_nas(file_data, owner_name, data_generator, file_type, chemistry, filename, len(file_data))
            except Exception as upload_error:
                logging.error(f"Error uploading file {filename}: {str(upload_error)}")
                return jsonify(message=f'Error uploading file {filename}'), 500

            # Collect metadata and insert into the database
            file_metadata = {
                'file_name': filename,
                'owner_name': owner_name,
                'label_name': label_name,
                'file_type': file_type,
                'data_generator': data_generator,
                'chemistry': chemistry,
                'upload_date': upload_date,
                'file_path': nas_file_path,
                'description': description,
                'file_size': len(file_data),
                'checksum': file_checksum
            }

            try:
                files_collection = get_files_collection()
                files_collection.insert_one(file_metadata)
                upload_results.append(f'{filename} uploaded successfully')
            except Exception as db_error:
                logging.error(f'Error inserting file data for {filename}: {str(db_error)}')
                return jsonify(message=f'Error inserting file data for {filename} into the database'), 500

        logging.info(f"File upload completed in {time.time() - start_time:.2f} seconds.")
        conn.close()
        return jsonify(message='Files uploaded successfully', results=upload_results), 201
    
    except Exception as upl:
        logging.error(f'Exception occurred during file upload: {str(upl)}')
        return jsonify(message=f'An error occurred: {str(upl)}')

# Function to search files in the database
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
        files_collection = get_files_collection()  # Get the MongoDB collection
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

# Function to download a file
def download_file(file_id):
    """
    Download a file by its ID.
    """
    logging.info(f"Attempting to download file with ID: {file_id}")
    try:
        # Validate the file ID
        if not ObjectId.is_valid(file_id):
            logging.warning("Invalid file ID format.")
            return jsonify(message="Invalid file ID"), 400

        # Retrieve file metadata from Database
        files_collection = get_files_collection()  # Get the MongoDB collection
        file_data = files_collection.find_one({'_id': ObjectId(file_id)})
        if not file_data:
            logging.warning(f"File not found for ID: {file_id}")
            return jsonify(message='File not found'), 404

        logging.info(f"File found: [{file_data['file_path']}]")

        # Retrieve NAS file path from metadata
        nas_file_path = file_data['file_path']

        # Establish SMB connection
        conn = establish_smb_connection()
        if not conn:
            logging.error("Failed to establish SMB connection.")
            return jsonify(message="Failed to connect to NAS"), 500

        # Fetch the file from the NAS
        file_obj = BytesIO()
        try:
            conn.retrieveFile(os.getenv('SMB_SHARE'), nas_file_path, file_obj)
            file_obj.seek(0)
            logging.info(f"File successfully retrieved from NAS: [{file_data['file_name']}]")
            return send_file(file_obj, 
                             as_attachment=True, 
                             download_name=file_data['file_name'],
                             mimetype='application/octet-stream'
            )
        except Exception as e:
            logging.error(f"Error downloading file from NAS: {str(e)}")
            return jsonify(message="Error downloading file from NAS"), 500
    except Exception as e:
        logging.error(f'Error downloading file: {str(e)}')
        return jsonify(message=f'Error downloading file: {str(e)}'), 500
