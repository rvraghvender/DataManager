import os
import time
import hashlib
from io import BytesIO
from backend.config.config import get_config
from backend.logger import logging
from bson.objectid import ObjectId
from backend.config.config import UPLOAD_FOLDER
from datetime import datetime
from smb.SMBConnection import SMBConnection
from dotenv import load_dotenv


load_dotenv(dotenv_path='../.env')
chunk_size = get_config()['UPLOAD_CHUNK_SIZE']  * 1024 *  1024
RETRY_LIMIT = 3
RETRY_DELAY = 2  # seconds between retries


# Function to verify checksum after file upload from NAS
def verify_file_checksum(conn, nas_file_path, expected_checksum, chunk_size=chunk_size):
    """
    Verify the checksum of the file stored on NAS by recalculating its checksum.
    """
    try:
        with BytesIO() as file_obj:
            conn.retrieveFile(os.getenv('SMB_SHARE'), nas_file_path, file_obj)
            file_obj.seek(0)
            # Recalculate the checksum of the uploaded file
            file_data = file_obj.read()
            actual_checksum = calculate_file_checksum(file_data, chunk_size)
            logging.debug(f"Checksum for {nas_file_path} is {actual_checksum}")

            # Compare the checksums
            if actual_checksum != expected_checksum:
                logging.error(f"Checksum mismatch for file {nas_file_path}. Expected: {expected_checksum}, Found: {actual_checksum}")
                return False
            return True
    except Exception as e:
        logging.error(f"Error verifying checksum for {nas_file_path}: {str(e)}")
        return False

def calculate_file_checksum(file_data, chunk_size=chunk_size):
    """
    Calculate MD5 checksum for file to verify integrity after upload.
    """
    hash_md5 = hashlib.md5()
    file_obj = BytesIO(file_data)
    while chunk := file_obj.read(chunk_size):
        hash_md5.update(chunk)
    return hash_md5.hexdigest() 

def establish_smb_connection():
    """
    Establish and return an SMB connection, with retry logic
    """
    smb_host = os.getenv('SMB_HOST')
    smb_share = os.getenv('SMB_SHARE')
    smb_user = os.getenv('SMB_USER')
    smb_password = os.getenv('SMB_PASSWORD')

    if not all([smb_host, smb_share, smb_user, smb_password]):
        logging.error("Missing SMB configuration in .env file")
        raise ValueError("Missing SMB configuration in .env file")

    conn = SMBConnection(smb_user, smb_password, 'client_machine_name', smb_host, domain='WORKGROUP', use_ntlm_v2=True)
    retry_count = 0
    while retry_count < RETRY_LIMIT:
        try:
            conn.connect(smb_host, 139)
            logging.info("SMB connection established successfully.")
            return conn
        except Exception as e:
            retry_count += 1
            logging.error(f"Error establishing SMB connection (Attemp {retry_count}/{RETRY_LIMIT}: {str(e)}")
            if retry_count == RETRY_LIMIT:
                logging.error("Exceed retry limit for SMB connection.")
            time.sleep(RETRY_DELAY)


def create_nas_directories(conn, nas_url):
    """
    Create required directories on the NAS server if they don't exist.
    """
    dirs = nas_url.strip("/").split("/")
    current_path = ""

    for dir in dirs:
        current_path = os.path.join(current_path, dir)
        try:
            # Check if the directory exists before attempting to create it
            conn.listPath(os.getenv('SMB_SHARE'), current_path)
            logging.debug(f"Directory {current_path} exists.")
        except Exception as list_error:
            # Directory does not exist, try to create it
            logging.warning(f"Directory {current_path} not found. Attempting to create it.")
            try:
                conn.createDirectory(os.getenv('SMB_SHARE'), current_path)
                logging.debug(f"Created directory: {current_path}")
            except Exception as create_error:
                # Log the error and continue, or raise if needed
                logging.error(f"Failed to create directory {current_path}: {str(create_error)}")
                # Optionally, raise the error if it's critical
                raise Exception(f"Critical error: Unable to create directory {current_path}") from create_error

    logging.info(f"Directory {nas_url} verified/created on NAS.")

def upload_to_nas(file_data, owner_name, data_generator, file_type, chemistry, filename, file_size):
    """
    Upload file to NAS with chunked buffered upload and error handling.
    """

    nas_url = f"/Arnad_Group_DATA/UPLOAD/{owner_name}/{data_generator}/{file_type}/{chemistry}/"
    destination_path = os.path.join(nas_url, filename)

    # Calculate file checksum before uploading
    try:
        file_checksum = calculate_file_checksum(file_data)
    except Exception as ff:
        raise ff

    conn = establish_smb_connection()
    create_nas_directories(conn, nas_url)

    file_exists = False
    try:
        file_list = conn.listPath(os.getenv('SMB_SHARE'), nas_url)
        file_exists = any(f.filename == filename for f in file_list)
    except Exception as ee:
        logging.error(f"Error listing files in {nas_url}: {str(ee)}")

    if file_exists:
        logging.error(f"File '{filename}' already exists on NAS at {nas_url}.")
        conn.close()
        raise FileExistsError(f"File '{filename}' already exists on NAS.")

    # Upload the file in a buffered manner to prevent memory overload for large files
    # Using a buffered upload method
    file_obj = BytesIO(file_data)
    bytes_uploaded = 0
    retry_count = 0
    file_obj.seek(0)  # Start reading from the beginning of the file

    # Using storeFile method to upload the whole file
    # with BytesIO(file_data) as file_data_obj:
    #    conn.storeFile(os.getenv('SMB_SHARE'), destination_path, file_data_obj)

    try:
        while chunk := file_obj.read(chunk_size):
            # Upload chunks in a loop
            chunk_uploaded = False
            retries = 0

            while not chunk_uploaded and retries < RETRY_LIMIT:
                try:
                    # Wrap the chunk in BytesIO and upload
                    with BytesIO(chunk) as chunk_obj:
                        conn.storeFileFromOffset(os.getenv('SMB_SHARE'), destination_path, chunk_obj, offset=bytes_uploaded)

                    # If upload is successful, update the progress
                    bytes_uploaded += len(chunk)
                    progress = (bytes_uploaded / file_size) * 100
                    logging.debug(f"Uploaded {bytes_uploaded} / {file_size} bytes -- {progress:.2f}% so far...")

                    # Mark the chunk as uploaded successfully
                    chunk_uploaded = True

                except Exception as e:
                    retries += 1
                    logging.warning(f"Error uploading chunk {bytes_uploaded}/{file_size}. Retry attempt {retries} of {RETRY_LIMIT}. Error: {e}")
                    if retries == RETRY_LIMIT:
                        logging.error(f"Failed to upload chunk {bytes_uploaded}/{file_size} after {RETRY_LIMIT} retries.")
                        raise  # Reraise the error after retry limit is exceeded

                    time.sleep(RETRY_DELAY)  # Wait before retrying

        logging.info(f"File [{filename}] uploaded successfully with {bytes_uploaded} bytes with {progress:.2f}%.")
    finally:
        # Post-upload checksum verification
        #if not verify_file_checksum(conn, destination_path, file_checksum):
        #   logging.error(f"Checksum mismatch for file {filename}. Upload may have failed or file is corrupted.")
        #   raise ValueError(f"Checksum mismatch for file {filename}. Upload may have failed or file is corrupted.")
        if conn:
            conn.close()


    return file_checksum, os.path.join(nas_url, filename)

