# Module Description: Get information related to floors climbed and descended on last day
# Author: Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber
# Date: 08.12.2023

__artifacts_v2__ = {
    "Garmin_Connect_Floors": {
        "name": "Garmin Floors",
        "description": "Extract information of Garmin Connect application",
        "author": "Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber",
        "version": "1.0",
        "date": "2023-12-05",
        "requirements": "none",
        "category": "Garmin Application",
        "notes": "",
        "paths": ('*/private/var/mobile/Containers/Data/Application/*/Library/Caches/com.pinterest.PINDiskCache.PINCacheShared/MyDayRealTimeDataService_realTimeFloorsCacheDataKey'),
        "function": "get_garmin_floors"
    }
}

import plistlib
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import tsv, convert_ts_human_to_utc, convert_utc_human_to_timezone
from datetime import datetime

def get_garmin_floors(files_found, report_folder, seeker, wrap_text, timezone_offset):
    # Create an empty list to store extracted data
    data_list = []
    # Convert elements to string
    for file_found in files_found:
        file_found = str(file_found)

        # Opening and loading the file
        with open(file_found, "rb") as file:
            content = plistlib.load(file)

            # Search for values with associated keys
            root = content['$top']['root']
            objects = content['$objects']

            # Search Values associated with floors
            value_key = objects[root]['valueKey']
            floors_data = objects[value_key]
            floors_descended_key = floors_data['floorsDescendedKey']
            floors_climbed_key = floors_data['floorsClimbedKey']
            floors_descended = objects[floors_descended_key]
            floors_climbed = objects[floors_climbed_key]

            # Search Date-related values
            date_key = objects[root]['dateKey']
            date_value = objects[date_key]['NS.time']

            # Date format conversion
            # 01.01.2001 because of the apple format (apple epoch)
            epoch_offset = datetime(2001, 1, 1).timestamp()
            adjusted_timestamp = date_value + epoch_offset
            date_object_utc = datetime.utcfromtimestamp(adjusted_timestamp)

            formatted_date = date_object_utc.strftime('%Y-%m-%d %H:%M:%S')
            start_time = convert_ts_human_to_utc(formatted_date)
            start_time = convert_utc_human_to_timezone(start_time, timezone_offset)

            # Adds values to report data_list
            data_list.append(('Date', start_time))
            data_list.append(('Floors_climbed', floors_climbed))
            data_list.append(('Floors_descended', floors_descended))

    # Generates report
    report = ArtifactHtmlReport('Garmin Floors')
    description = "Floors climbed and descended on last day"
    report.start_artifact_report(report_folder, 'Garmin_Floors', description)
    report.add_script()
    data_headers = ('Key', 'Value')
    report.write_artifact_data_table(data_headers, data_list, file_found)
    report.end_artifact_report()

    # Generates TSV file
    tsvname = 'Garmin_Floors'
    tsv(report_folder, data_headers, data_list, tsvname)

    # Nothing is inserted in timeline because there are no time-stamped records