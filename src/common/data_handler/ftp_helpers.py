import datetime
from operator import itemgetter
import csv
import pandas as pd
from google.cloud import storage
from common.data_handler.ftp_file_headers import headers


def get_report_metadata(filename):
    file_bits = filename.split('.')
    report_account = file_bits[0]
    report_type = file_bits[1]
    report_from_date = file_bits[2]
    report_to_date = file_bits[3]

    payload = {
        'file': filename,
        # 'account': report_account,
        'type': report_type,
        'report_start': report_from_date,
        'report_end': report_to_date
    }

    return payload


def convert_date_from_int(date_input):
    year = int(date_input[:4])
    month = int(date_input[4:6])
    day = int(date_input[6:8])
    date = datetime.date(year, month, day)
    return date


def get_most_recent_file(file_list):
    relevant_files = []
    for record in file_list:
        file_end_date = convert_date_from_int(record.split('.')[3])
        tupe = (record, file_end_date)
        relevant_files.append(tupe)
    most_recent_file = max(relevant_files, key=itemgetter(1))[0]
    return most_recent_file


def get_current_files(file_list: list, exclude_type: list = None, use_full_hist: bool = True):
    if exclude_type is None:
        exclude_type = []
    audit_type_year, current_files = [], []
    file_bits = [i.split('.') for i in file_list]

    # Get distinct combos and append to audit_type_year
    for file in file_bits:
        account = file[0]
        report_type = file[1]
        from_date = file[2]
        to_date = file[3]
        year = from_date[:4]

        if (report_type, year) not in audit_type_year:
            audit_type_year.append((report_type, year))

    # Get max file for each entry in audit_type_year
    for distinct_type_year in audit_type_year:
        dist_type = distinct_type_year[0]
        dist_year = distinct_type_year[1]

        tmp = []
        for file in file_bits:
            account = file[0]
            report_type = file[1]
            from_date = file[2]
            to_date = file[3]
            year = from_date[:4]

            if dist_type == report_type and dist_year == year and dist_type not in exclude_type:
                tmp.append(file)
        current_file = '.'.join(max(tmp, key=itemgetter(3)))
        current_files.append(current_file)  # TODO: test once 2020 files are uploaded

    return sorted(current_files)


def get_report_data(report, report_type):
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


def upload_file_to_gcp(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )
