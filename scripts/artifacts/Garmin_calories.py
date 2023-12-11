__artifacts_v2__ = {
    "Garmin_Connect_Calories": {
        "name": "Garmin Connect Calories",
        "description": "Get information related to calories burned on last day",
        "author": "Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber",
        "version": "1.0",
        "date": "2023-12-12",
        "requirements": "none",
        "category": "Garmin Application",
        "notes": "",
        "paths": ('*/private/var/mobile/Containers/Data/Application/*/Library/Caches/com.pinterest.PINDiskCache.PINCacheShared/MyDayRealTimeDataService_realTimeCaloriesCacheDataKey'),
        "function": "get_garmin_calories"
    }
}

import plistlib
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import tsv, convert_ts_human_to_utc, convert_utc_human_to_timezone
from datetime import datetime

def get_garmin_calories(files_found, report_folder, seeker, wrap_text, timezone_offset):
    # Create an empty list to store extracted data
    data_list = []
    # Convert elements to string
    for file_found in files_found:
        file_found = str(file_found)

        # Opening and loading the file
        with open(file_found, "rb") as fp:
            content = plistlib.load(fp)

            # Search for values with associated keys
            root = content['$top']['root']
            objects = content['$objects']

            # Search Calorie values
            value_key = objects[root]['valueKey']
            real_time_calorie_data = objects[value_key]
            active_calories_key = real_time_calorie_data['activeCaloriesKey']
            total_calories_key = real_time_calorie_data['totalCaloriesKey']
            active_calories = objects[active_calories_key]
            total_calories = objects[total_calories_key]

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
            data_list.append(('Active Calories', active_calories))
            data_list.append(('Total Calories', total_calories))

        # Generates report
        report = ArtifactHtmlReport('Garmin Calories')
        description = "Calories burned on last day"
        report.start_artifact_report(report_folder, 'Garmin_Calories', description)
        report.add_script()
        data_headers = ('Key', 'Value')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()

        # Generates TSV file
        tsvname = 'Garmin_Calories'
        tsv(report_folder, data_headers, data_list, tsvname)

        # Nothing is inserted in timeline because there are no time-stamped records