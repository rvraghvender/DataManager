from flask import request, jsonify, send_from_directory, send_file
from werkzeug.utils import secure_filename
from backend.models.file_model import get_files_collection
from io import BytesIO
import os
from backend.logger import logging
from bson.objectid import ObjectId
from backend.config.config import UPLOAD_FOLDER
from datetime import datetime
from smb.SMBConnection import SMBConnection
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env')


def upload_to_nas(local_file_path, owner_name, data_generator, file_type, chemistry):

    # Retrieve SMB connection parameters from environment variables
    smb_host = os.getenv('SMB_HOST')
    smb_share = os.getenv('SMB_SHARE')
    smb_user = os.getenv('SMB_USER')
    smb_password = os.getenv('SMB_PASSWORD')

    if not all([smb_host, smb_share, smb_user, smb_password]):
        logging.error("Missing SMB configuration in .env file")
        raise ValueError("Missing SMB configuration in .env file")

    # Define the nas folder path
    nas_url = f"/Arnad_Group_DATA/UPLOAD/{owner_name}/{data_generator}/{file_type}/{chemistry}/"
    
    # Secure filename
    filename = os.path.basename(local_file_path)
    destination_path = os.path.join(nas_url, filename)
    
    # Establish SMB connection
    conn = SMBConnection(smb_user, smb_password, 'client_machine_name', smb_host, domain='WORKGROUP', use_ntlm_v2=True)
    conn.connect(smb_host, 139)  # 139 is the default SMB port for NetBIOS over TCP/IP

    dirs = nas_url.strip("/").split("/")
    
    # Start with an empty path and progressively build it
    current_path = ""
    
    for dir in dirs:
        current_path = f"{current_path}/{dir}" if current_path else dir
        try:
            # Check if the directory already exists by listing the contents of the current path
            try:
                # Try listing the contents of the current directory
                conn.listPath(smb_share, current_path)
                logging.debug(f"Directory {current_path} already exists.")
            except Exception as e:
                # If listing the directory fails, create it
                conn.createDirectory(smb_share, current_path)
                logging.debug(f"Directory {current_path} created successfully.")
        except Exception as e:
            logging.error(f"Failed to create or check directory {current_path}: {str(e)}")
            # Handle error gracefully, continue to the next directory
            pass
    logging.info(f"Directory {nas_url} created successfully on nas.")

    # Now upload the file to the nas
    with open(local_file_path, 'rb') as file_obj:
        conn.storeFile(smb_share, os.path.join(nas_url, filename), file_obj)

    logging.info(f"File {filename} successfully uploaded to nas at {nas_url}")

    conn.close()
    return os.path.join(nas_url, filename)

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
            
            owner_name = request.form['owner_name']
            label_name = request.form['label_name']
            file_type = request.form['file_type']
            data_generator = request.form['data_generator']
            chemistry = request.form['chemistry']
            file_date = request.form['upload_date']
            description = request.form['description']
            filename = secure_filename(file.filename)

            # Save the file to the server
            folder_path = os.path.abspath(os.path.join(
                UPLOAD_FOLDER,
                owner_name,
                data_generator,
                file_type,
                chemistry))
            os.makedirs(folder_path, exist_ok=True)
            file_path = os.path.join(folder_path, filename)
            file.save(file_path)
            
            # Convert upload_date to a datetime object
            try:
                upload_date = datetime.strptime(file_date, '%Y-%m-%d')  # Convert to datetime
            except ValueError:
                return jsonify(message='Invalid date format. Use YYYY-MM-DD'), 400

            # Upload the file to the NAS and get the NAS path
            nas_file_path = upload_to_nas(file_path, owner_name, data_generator, file_type, chemistry)
            
            # Collect metadata
            file_data = {
                'file_name' : filename,
                'owner_name':owner_name,
                'label_name' : label_name,
                'file_type': file_type,
                'data_generator' : data_generator,
                'chemistry' : chemistry,
                'upload_date': upload_date,
                'file_path': nas_file_path,
                'description' : description,
                'file_size' : os.path.getsize(file_path) ##
            }

            try:
                files_collection = get_files_collection()  # Get the MongoDB collection
                files_collection.insert_one(file_data)
                upload_results.append(f'{filename} uploaded successfully')
            except Exception as e:
                logging.error(f'Error inserting file data for {filename}: {str(e)}')
                return jsonify(message=f'Error inserting file data for {filename} into the database'), 500
        
            os.remove(file_path)
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

def download_file(file_id):
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

        logging.info(f"File found: {file_data['file_path']}")

        # Retrieve nas file path from metadata
        nas_file_path = file_data['file_path']

        smb_host = os.getenv('SMB_HOST')
        smb_share = os.getenv('SMB_SHARE')
        smb_user = os.getenv('SMB_USER')
        smb_password = os.getenv('SMB_PASSWORD')

        if not all([smb_host, smb_share, smb_user, smb_password]):
            logging.error("Missing SMB configuration in .env file")
            return jsonify(message="Missing SMB configuration in .env file"), 500

        # Establish SMB connection
        conn = SMBConnection(smb_user, smb_password, 'client_machine_name', smb_host, domain='WORKGROUP', use_ntlm_v2=True)
        conn.connect(smb_host, 139)  # 139 is the default SMB port for NetBIOS over TCP/IP

        # Fetch the file from the nas
        try:
            file_name = os.path.basename(nas_file_path)
            file_obj = BytesIO()
            conn.retrieveFile(smb_share, nas_file_path, file_obj)
            file_obj.seek(0)  # Move the cursor to the beginning of the file
            conn.close()

            # Serve the file as a downloadable response
            return send_file(file_obj, as_attachment=True, download_name=file_name)

        except Exception as e:
            logging.error(f"Error retrieving file from nas: {str(e)}")
            conn.close()
            return jsonify(message="Error retrieving file from nas"), 500

    except Exception as e:
        logging.error(f"Error downloading file: {str(e)}")
        return jsonify(message=f'Error downloading file: {str(e)}'), 500
