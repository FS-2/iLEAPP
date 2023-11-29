# Module Description: Parses Garmin Connect details
# Author: Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber
# Date: 05.12.2023

__artifacts_v2__ = {
    "Garmin_Connect": {
        "name": "Garmin Connect",
        "description": "Extract information of Garmin Connect application",
        "author": "Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber",
        "version": "1.0",
        "date": "2023-12-05",
        "requirements": "none",
        "category": "Application",
        "notes": "",
        "paths": ('*/private/var/mobile/Containers/Data/Application/*/Library/Caches/com.pinterest.PINDiskCache.PINCacheShared/MyDayRealTimeDataService_realTimeCaloriesCacheDataKey'),
        "function": "get_garmin"
    }
}
            #peut avoir plusieurs paths car tuple


import plistlib

import plistlib
from scripts.artifact_report import ArtifactHtmlReport
import pytz
from datetime import datetime
from scripts.ilapfuncs import tsv
from scripts.ilapfuncs import timeline


def get_garmin(files_found, report_folder, seeker, wrap_text, timezone_offset):
    data_list = []

    for file_found in files_found:
        file_found = str(file_found)

        with open(file_found, "rb") as fp:
            contenu = plistlib.load(fp)

            active_calories = contenu['$objects'][contenu['$objects'][contenu['$objects'][contenu['$top']['root']]['valueKey']]['activeCaloriesKey']]['value']
            total_calories = contenu['$objects'][contenu['$objects'][contenu['$objects'][contenu['$top']['root']]['valueKey']]['totalCaloriesKey']]['value']
            date_value = contenu['$objects'][contenu['$objects'][contenu['$top']['root']]['dateKey']]['NS.time']

            epoch_offset = datetime(2001, 1, 1).timestamp()
            adjusted_timestamp = date_value + epoch_offset

            date_object_utc = datetime.utcfromtimestamp(adjusted_timestamp)
            fuseau_horaire = pytz.timezone('Europe/Paris')
            date_object = date_object_utc.replace(tzinfo=pytz.utc).astimezone(fuseau_horaire)

            date_formattee = date_object.strftime('%d.%m.%Y %H:%M:%S')



            data_list.append(('Date', date_formattee))
            data_list.append(('Active Calories', active_calories))
            data_list.append(('Total Calories', total_calories))

    report = ArtifactHtmlReport('Garmin')
    report.start_artifact_report(report_folder, 'Garmin')
    report.add_script()
    data_headers = ('Key', 'Values')
    report.write_artifact_data_table(data_headers, data_list, file_found)

    tsvname = 'Garmin'
    tsv(report_folder, data_headers, data_list, tsvname)

    tlactivity = 'Garmin'
    timeline(report_folder, tlactivity, data_list, data_headers)

    report.end_artifact_report()
