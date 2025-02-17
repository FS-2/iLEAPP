__artifacts_v2__ = {
    "Garmin_Connect_Download": {
        "name": "Garmin Download",
        "description": "Get information about the Garmin Connect Application",
        "author": "Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber",
        "version": "1.0",
        "date": "2023-12-12",
        "requirements": "none",
        "category": "Garmin Application",
        "notes": "",
        "paths": ('*/private/var/containers/Bundle/Application/*/iTunesMetadata.plist', '*/private/var/mobile/Containers/Data/Application/*/Library/Caches/com.crashlytics.data/com.garmin.connect.mobile/v5/settings/cache-key.json'),
        "function": "get_garmin_download"
    }
}

import plistlib
import json
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import tsv, convert_ts_human_to_utc, convert_utc_human_to_timezone
from datetime import datetime

def get_garmin_download(files_found, report_folder, seeker, wrap_text, timezone_offset):
    # Create an empty list to store extracted data
    data_list = []
    # Convert elements to string
    for file_found in files_found:
        file_found = str(file_found)

        # For the first file (plist xml format)
        if file_found.endswith('iTunesMetadata.plist'):

            # Opening and loading the file
            with open(file_found, "rb") as file:
                content = plistlib.load(file)

                # Search for values with associated keys
                apple_id = content['com.apple.iTunesStore.downloadInfo']['accountInfo']['AppleID']
                purchaseDate = content['com.apple.iTunesStore.downloadInfo']['purchaseDate']

                # Date format conversion
                if purchaseDate.endswith('Z'):
                    purchaseDate = purchaseDate[:-1] + '+00:00'

                # Manages seconds with a decimal
                if '.' in purchaseDate:
                    parts = purchaseDate.split('.')
                    purchaseDate = parts[0] + '.' + parts[1][:6]  # Keep maximum 6 digits after decimal
                date_object = datetime.fromisoformat(purchaseDate)
                formatted_date = date_object.strftime('%Y-%m-%d %H:%M:%S')
                start_time = convert_ts_human_to_utc(formatted_date)
                start_time = convert_utc_human_to_timezone(start_time, timezone_offset)

                # Adding values to report data_list
                data_list.append(('Apple ID', apple_id))
                data_list.append(('Application download date', start_time))


        # For the second file (json format)
        if file_found.endswith('cache-key.json'):
            with open(file_found, 'r') as file:
                content = json.load(file)

                # Search for values with associated keys
                app_version = content['app_version']
                google_app_id = content['google_app_id']

                # Adding values to report data_list
                data_list.append(('App version', app_version))
                data_list.append(('App ID', google_app_id))

    # Generates report
    report = ArtifactHtmlReport('Garmin Download')
    description = "Information about the Garmin Connect Application"
    report.start_artifact_report(report_folder, 'Garmin_Download', description)
    report.add_script()
    data_headers = ('Key', 'Value')
    report.write_artifact_data_table(data_headers, data_list, file_found)
    report.end_artifact_report()

    # Generates TSV file
    tsvname = 'Garmin_Download'
    tsv(report_folder, data_headers, data_list, tsvname)

    # Nothing is inserted in timeline because there are no time-stamped records