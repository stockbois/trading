import os
import datetime
from ftplib import FTP
from operator import itemgetter
import subprocess
import csv
import pandas as pd
import logging
from common.utils.logging import setupLogger

# Get config
FTP_HOST = os.getenv('FTP_HOST')
FTP_USERNAME = os.getenv('FTP_USERNAME')
FTP_PASSWORD = os.getenv('FTP_PASSWORD')
GPG_PASSWORD = os.getenv('GPG_PASSWORD')
FTP_WORKING_DIR = 'outgoing'
LOCAL_GNUPGHOME_DIR = os.getenv('LOCAL_GNUPGHOME_DIR')
LOCAL_DATA_DIR = os.getenv('LOCAL_DATA_DIR')


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


def process_report(report):
    content = []
    with open(report, newline='') as f:
        file_data = csv.reader(f, delimiter='|')
        row_count = 0
        for row in file_data:
            if row_count == 0:
                headers = row
            elif row_count > 0 and row[0][0] == 'U':
                content.append(row)
            row_count += 1
        df = pd.DataFrame(data=content, columns=headers)
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

    download_audit = []

    # Download encrypted files from FTP server
    for report_type in report_types:
        report = get_most_recent_file(files, report_type)

        try:
            with open(LOCAL_DATA_DIR + '/encryp' + '/' + report, 'wb') as f:
                ftp.retrbinary('RETR ' + report, f.write)
            download_audit.append(report)
        except:
            print("Error downloading {f}".format(f=report))

    # Be polite - close the connection
    ftp.quit()

    # Clear unencrypted folder
    unencryp_folder_contents = LOCAL_DATA_DIR + '/unencryp/*'
    run_str = f'rm -rf {unencryp_folder_contents}'
    subprocess.call(run_str, shell=True)

    # Decrypt files in decryp folder and drop in unencryp folder
    for report in download_audit:

        encryp_f = LOCAL_DATA_DIR + '/encryp/{file}'.format(file=report)
        decryp_f = LOCAL_DATA_DIR + '/unencryp/{file}'.format(
            file='.'.join(report.split('.')[:-1])
        )

        run_str = f'gpg -d --pinentry-mode=loopback --passphrase {GPG_PASSWORD} --output {decryp_f} {encryp_f}'
        subprocess.call(run_str, shell=True)

    # Process the unencrypted files
    for report in download_audit:
        path = LOCAL_DATA_DIR + '/unencryp/{file}'.format(
            file='.'.join(report.split('.')[:-1])
        )
        data = process_report(path)
        print(data)