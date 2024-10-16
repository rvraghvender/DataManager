from flask import request, jsonify, send_from_directory
from models.file_model import files_collection
from middleware.file_upload import upload_file_handler
import os
import logging
from bson.objectid import ObjectId


def upload_file():
    if 'file' not in request.files:
        return jsonify(message='No file part'), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify(message='No selected file'), 400

    # Save the file to the server
    file_path = f"./uploads/{file.filename}"
    file.save(file_path)

    # Collect metadata
    owner_name = request.form.get('owner_name')
    file_type = request.form.get('file_type')
    upload_date = request.form.get('upload_date')

    # Insert metadata into the database
    file_data = {
        'filename': file.filename,
        'owner_name': owner_name,
        'file_type': file_type,
        'upload_date': upload_date,
        'file_path': file_path,  # Store the file path if needed for downloads
    }

    try:
        files_collection.insert_one(file_data)
    except Exception as e:
        return jsonify(message=f'Error inserting file data into the database: {str(e)}'), 500

    return jsonify(message='File uploaded successfully'), 201


def search_files():
    owner_name = request.args.get('owner_name')
    file_type = request.args.get('file_type')
    upload_date = request.args.get('upload_date')

    # Construct your query based on provided parameters
    query = {}
    if owner_name:
        query['owner_name'] = owner_name
    if file_type:
        query['file_type'] = file_type
    if upload_date:
        query['upload_date'] = upload_date

    # Query the database
    try:
        files = files_collection.find(query)  # Adjust based on your database logic

        results = []
        for file in files:
            results.append({
                'id': str(file['_id']),  # Include the file ID for downloads
                'filename': file['filename'],
                'owner_name': file['owner_name'],
                'file_type': file['file_type'],
                'upload_date': file['upload_date'],
            })

        return jsonify(results), 200
    except Exception as e:
        return jsonify(message=f'Error searching for files: {str(e)}'), 500



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
        return send_from_directory(
            os.path.dirname(file_data['file_path']),
            os.path.basename(file_data['file_path']),
            as_attachment=True
        )
    except Exception as e:
        logging.error(f"Error downloading file: {str(e)}")
        return jsonify(message=f'Error downloading file: {str(e)}'), 500
