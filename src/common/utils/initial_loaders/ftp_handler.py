import os
import datetime
from ftplib import FTP
from operator import itemgetter
import subprocess
import csv
import pandas as pd
import logging
from common.utils.storage import upload_file
from common.utils.logging import setupLogger
from common.utils.initial_loaders.ftp_file_headers import headers

# Get config
FTP_HOST = os.getenv('FTP_HOST')
FTP_USERNAME = os.getenv('FTP_USERNAME')
FTP_PASSWORD = os.getenv('FTP_PASSWORD')
GPG_PASSWORD = os.getenv('GPG_PASSWORD')
FTP_WORKING_DIR = 'outgoing'
LOCAL_GNUPGHOME_DIR = os.getenv('LOCAL_GNUPGHOME_DIR')
LOCAL_DATA_DIR = os.getenv('LOCAL_DATA_DIR')
GCP_STORAGE_BUCKET = os.getenv('GCP_STORAGE_BUCKET')


def convert_date_from_int(date_input):
    year = int(date_input[:4])
    month = int(date_input[4:6])
    day = int(date_input[6:8])
    date = datetime.date(year, month, day)
    return date


def get_account_list(files):
    accounts = []
    for f in files:
        account = f.split('.')[0]
        if account not in accounts:
            accounts.append(account)
    return accounts


def get_most_recent_file(file_list, file_type):
    relevant_files = []
    for record in file_list:
        if file_type in record:
            file_end_date = convert_date_from_int(record.split('.')[3])
            tupe = (record, file_end_date)
            relevant_files.append(tupe)
    most_recent_file = max(relevant_files, key=itemgetter(1))[0]
    return most_recent_file


def get_report_metadata(filename):
    report_account = filename.split('.')[0]
    report_type = filename.split('.')[1]
    report_from_date = filename.split('.')[2]
    report_to_date = filename.split('.')[3]

    payload = {
        'file': filename,
        'account': report_account,
        'type': report_type,
        'report_start': report_from_date,
        'report_end': report_to_date
    }

    return payload


def process_report(report, report_type):
    content = []
    with open(report, newline='') as f:
        file_data = csv.reader(f, delimiter='|')
        row_count = 0
        for row in file_data:
            if row[0][0] == 'U':
                content.append(row)
            row_count += 1
        df = pd.DataFrame(data=content, columns=headers[report_type])
    return df.to_json(orient='records')


def retrieve_latest_batch():
    setupLogger(logging_level=logging.INFO)

    # Login to FTP and navigate to working directory
    logging.info('Running FTP processing script')
    ftp = FTP(FTP_HOST)
    ftp.login(user=FTP_USERNAME, passwd=FTP_PASSWORD)
    ftp.cwd(FTP_WORKING_DIR)
    logging.info('Connected to FTP server')

    # Get the full list of files in the directory
    files = ftp.nlst()

    # Specify desired report types and download the most recent of each
    report_types = [
        'CashReport',
        'OpenPositions',
        'PnLDetails',
        'TradeConfirmExecutions'
    ]

    encrypted_file_downloads = []

    # Download most recent encrypted files from FTP server
    for report_type in report_types:
        report = get_most_recent_file(files, report_type)

        try:
            with open(LOCAL_DATA_DIR + '/encryp' + '/' + report, 'wb') as f:
                ftp.retrbinary('RETR ' + report, f.write)
            logging.info(f'Downloaded {report} from FTP server')
            encrypted_file_downloads.append(report)
        except:
            print("Error downloading {f}".format(f=report))

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
