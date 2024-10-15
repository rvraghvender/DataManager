from flask import request, jsonify, send_from_directory
from models.file_model import files_collection
from middleware.file_upload import upload_file_handler
import os
from bson.objectid import ObjectId

def upload_file():
    if 'file' not in request.files:
        return jsonify(message='No file part'), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify(message='No selected file'), 400
    
    # Save the file to the server and add details to the database
    # Example code to save file:
    file.save(f"./uploads/{file.filename}")
    
    # You would also insert metadata into the database here
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
    files = files_collection.find(query)  # Adjust based on your database logic

    results = []
    for file in files:
        results.append({
            'filename': file['filename'],
            'owner_name': file['owner_name'],
            'file_type': file['file_type'],
            'upload_date': file['upload_date'],
        })

    return jsonify(results), 200


#def upload_file():
#    file_data = upload_file_handler()
#    if isinstance(file_data, dict):
#        return jsonify(file_data), 201
#    return file_data  # Error response

#def search_files():
#    query = {k: v for k, v in request.args.items() if v}
#    files = list(files_collection.find(query))
#    for file in files:
#        file['_id'] = str(file['_id'])  # Convert ObjectId to string
#    return jsonify(files), 200

def download_file(file_id):
    file_data = files_collection.find_one({'_id': ObjectId(file_id)})
    if not file_data:
        return jsonify(message='File not found'), 404
    return send_from_directory(os.path.dirname(file_data['file_path']), os.path.basename(file_data['file_path']), as_attachment=True)

