from flask import Blueprint
from controllers.file_controller import upload_file, search_files, download_file
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

file_bp = Blueprint('files', __name__)

@file_bp.route('/upload', methods=['POST'])
def upload_file_route():
    """
    Handles the file upload process.

    Expects a file to be sent in the request.
    Returns a success message with the file ID or an error message.
    """
    try:
        logging.info("Uploading file...")
        return upload_file()
    except Exception as e:
        logging.error(f"Error uploading file: {str(e)}")
        return {"error": str(e)}, 500  # Return a 500 Internal Server Error with the error message

@file_bp.route('/search', methods=['GET'])
def search_files_route():
    """
    Handles file search requests.

    Expects query parameters to search for files.
    Returns a list of files that match the search criteria or an error message.
    """
    try:
        logging.info("Searching for files...")
        return search_files()
    except Exception as e:
        logging.error(f"Error searching for files: {str(e)}")
        return {"error": str(e)}, 500  # Return a 500 Internal Server Error with the error message

@file_bp.route('/download/<file_id>', methods=['GET'])
def download_file_route(file_id):
    """
    Handles file download requests.

    Expects a file ID as a path parameter.
    Returns the requested file or an error message if not found.
    """
    try:
        logging.info(f"Downloading file with ID: {file_id}...")
        return download_file(file_id)
    except Exception as e:
        logging.error(f"Error downloading file with ID {file_id}: {str(e)}")
        return {"error": str(e)}, 500  # Return a 500 Internal Server Error with the error message

