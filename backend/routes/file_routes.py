from flask import Blueprint
from controllers.file_controller import upload_file, search_files, download_file

file_bp = Blueprint('files', __name__)


#@file_bp.route('/upload', methods=['POST'])
#def upload_file_route():
#    return upload_file()

#file_bp.route('/upload', methods=['POST'])(upload_file)
#file_bp.route('/search', methods=['GET'])(search_files)
#file_bp.route('/download/<file_id>', methods=['GET'])(download_file)

@file_bp.route('/upload', methods=['POST'])
def upload_file_route():
    return upload_file()

@file_bp.route('/search', methods=['GET'])
def search_files_route():
    return search_files()

@file_bp.route('/download/<file_id>', methods=['GET'])
def download_file_route(file_id):
    return download_file(file_id)

