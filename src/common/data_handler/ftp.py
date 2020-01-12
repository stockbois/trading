import os
from ftplib import FTP
import subprocess
import logging
from common.data_handler.ftp_helpers import *

# Get config
FTP_HOST = os.getenv('FTP_HOST')
FTP_USERNAME = os.getenv('FTP_USERNAME')
FTP_PASSWORD = os.getenv('FTP_PASSWORD')
GPG_PASSWORD = os.getenv('GPG_PASSWORD')
LOCAL_DATA_DIR = os.getenv('LOCAL_DATA_DIR')
GCP_STORAGE_BUCKET = os.getenv('GCP_STORAGE_BUCKET')

download_audit = []
data = {}


def get_data():
    # Login to FTP and navigate to working directory
    logging.info('Running FTP processing script')
    ftp = FTP(FTP_HOST)
    ftp.login(user=FTP_USERNAME, passwd=FTP_PASSWORD)
    logging.info('Connected to FTP server')
    ftp.cwd('outgoing')

    # Get the full list of files in the directory
    files = ftp.nlst()

    # Download most recent encrypted files from FTP server
    current_files = get_current_files(files)
    for i in current_files:
        logging.info(f'Downloading from FTP: {i}')

    for current_file in current_files:
        try:
            with open(LOCAL_DATA_DIR + '/encryp/' + current_file, 'wb') as f:
                ftp.retrbinary('RETR ' + current_file, f.write)
            download_audit.append(current_file)
        except:
            logging.error(f"Error downloading {current_file}")
    logging.info('Finished downloading files from FTP')

    # Be polite - close the connection
    ftp.quit()

    # Clear unencrypted folder
    run_str = f'rm -rf {LOCAL_DATA_DIR}/unencryp/*'
    subprocess.call(run_str, shell=True)

    # Decrypt files in decryp folder and drop in unencryp folder
    for encrypted_download in download_audit:
        # Get filenames and filepaths
        encryp_f = encrypted_download
        decryp_f = '.'.join(encrypted_download.split('.')[:-1])
        encryp_fp = LOCAL_DATA_DIR + f'/encryp/{encryp_f}'
        decryp_fp = LOCAL_DATA_DIR + f'/unencryp/{decryp_f}'

        # Run decrypt subprocess
        run_str = f'gpg -d --pinentry-mode=loopback --passphrase {GPG_PASSWORD} --output {decryp_fp} {encryp_fp}'
        subprocess.call(run_str, shell=True)

        # Upload both unencryp and decryp files to google cloud bucket
        upload_file_to_gcp(GCP_STORAGE_BUCKET, encryp_fp, f'ibkr-ftp/encryp/{encryp_f}')
        upload_file_to_gcp(GCP_STORAGE_BUCKET, decryp_fp, f'ibkr-ftp/decryp/{decryp_f}')

        # Append to data out object (dict)
        report_metadata = get_report_metadata(decryp_f)
        report_type = report_metadata['type']

        try:
            data[report_type]['data'].extend(get_report_data(decryp_fp, report_type))
            data[report_type]['metadata'] = get_report_metadata(decryp_f)
        except KeyError:
            data[report_type] = {}
            data[report_type]['data'] = get_report_data(decryp_fp, report_type)
            data[report_type]['metadata'] = get_report_metadata(decryp_f)

    return data
