import os
from ftplib import FTP
import subprocess
import logging
from common.utils.storage import upload_file
from common.utils.logging import setupLogger
from common.utils.ftp_handler.helpers import get_current_files, process_report

# Get config
FTP_HOST = os.getenv('FTP_HOST')
FTP_USERNAME = os.getenv('FTP_USERNAME')
FTP_PASSWORD = os.getenv('FTP_PASSWORD')
GPG_PASSWORD = os.getenv('GPG_PASSWORD')
FTP_WORKING_DIR = 'outgoing'
LOCAL_GNUPGHOME_DIR = os.getenv('LOCAL_GNUPGHOME_DIR')
LOCAL_DATA_DIR = os.getenv('LOCAL_DATA_DIR')
GCP_STORAGE_BUCKET = os.getenv('GCP_STORAGE_BUCKET')


def run():
    setupLogger(logging_level=logging.INFO)

    # Login to FTP and navigate to working directory
    logging.info('Running FTP processing script')
    ftp = FTP(FTP_HOST)
    ftp.login(user=FTP_USERNAME, passwd=FTP_PASSWORD)
    ftp.cwd(FTP_WORKING_DIR)
    logging.info('Connected to FTP server')

    # Get the full list of files in the directory
    files = ftp.nlst()

    encrypted_file_downloads = []

    # Download most recent encrypted files from FTP server
    current_files = get_current_files(files)

    for current_file in current_files:
        try:
            with open(LOCAL_DATA_DIR + '/encryp/' + current_file, 'wb') as f:
                ftp.retrbinary('RETR ' + current_file, f.write)
            logging.info(f'Downloaded {current_file} from FTP server')
            encrypted_file_downloads.append(current_file)
        except:
            print("Error downloading {f}".format(f=current_file))

    # Be polite - close the connection
    ftp.quit()

    # Clear unencrypted folder
    unencryp_folder_contents = LOCAL_DATA_DIR + '/unencryp/*'
    run_str = f'rm -rf {unencryp_folder_contents}'
    subprocess.call(run_str, shell=True)

    data = {}

    # Decrypt files in decryp folder and drop in unencryp folder
    for encrypted_download in encrypted_file_downloads:
        # Get filenames
        encryp_f = encrypted_download
        decryp_f = '.'.join(encrypted_download.split('.')[:-1])
        # Use filenames to get local filepaths
        encryp_fp = LOCAL_DATA_DIR + f'/encryp/{encryp_f}'
        decryp_fp = LOCAL_DATA_DIR + f'/unencryp/{decryp_f}'
        # Run decrypt subprocess
        run_str = f'gpg -d --pinentry-mode=loopback --passphrase {GPG_PASSWORD} --output {decryp_fp} {encryp_fp}'
        subprocess.call(run_str, shell=True)
        # Upload both unencryp and decryp files to google cloud bucket
        upload_file(GCP_STORAGE_BUCKET, encryp_fp, f'ibkr-ftp/encryp/{encryp_f}')
        upload_file(GCP_STORAGE_BUCKET, decryp_fp, f'ibkr-ftp/decryp/{decryp_f}')
        # Generate metadata for unencrypted output
        file_split = decryp_f.split('.')
        report_type = file_split[-4]
        from_date = file_split[-3]
        to_date = file_split[-2]
        # Append to data out object (dict)
        data[report_type] = {}
        data[report_type]['metadata'] = {
            'from_date': from_date,
            'to_date': to_date
        }
        data[report_type]['data'] = process_report(decryp_fp, report_type)

    return data
