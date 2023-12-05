# Module Description: Parses Garmin Connect details
# Author: Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber
# Date: 05.12.2023

__artifacts_v2__ = {
    "Garmin_Connect_Calories": {
        "name": "Garmin Connect Calories",
        "description": "Extract information of Garmin Connect application",
        "author": "Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber",
        "version": "1.0",
        "date": "2023-12-05",
        "requirements": "none",
        "category": "Application",
        "notes": "",
        "paths": ('*/private/var/mobile/Containers/Data/Application/*/Library/Caches/com.pinterest.PINDiskCache.PINCacheShared/MyDayRealTimeDataService_realTimeCaloriesCacheDataKey'),
        "function": "get_garmin_calories"
    }
}

import plistlib

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, convert_ts_human_to_utc, convert_utc_human_to_timezone, logdevinfo
import pytz
from datetime import datetime
from scripts.ilapfuncs import tsv
from scripts.ilapfuncs import timeline

def get_garmin_calories(files_found, report_folder, seeker, wrap_text, timezone_offset):
    # Liste utilisée pour stocker les données extraites
    data_list = []
    # Conversion des éléments en string
    file_found = str(files_found[0])

    # Ouverture et chargement du fichier
    with open(file_found, "rb") as fp:
        contenu = plistlib.load(fp)

        # Recherche des valeurs avec les clés associées
        root = contenu['$top']['root']
        objects = contenu['$objects']

        # Valeurs associées aux calories
        value_key = objects[root]['valueKey']
        real_time_calorie_data = objects[value_key]
        active_calories_key = real_time_calorie_data['activeCaloriesKey']
        total_calories_key = real_time_calorie_data['totalCaloriesKey']
        active_calories = objects[active_calories_key]
        total_calories = objects[total_calories_key]

        # Valeurs associées à la date
        date_key = objects[root]['dateKey']
        date_value = objects[date_key]['NS.time']

        # Conversion du format de la date
        epoch_offset = datetime(2001, 1, 1).timestamp() #format de date apple
        adjusted_timestamp = date_value + epoch_offset
        date_object_utc = datetime.utcfromtimestamp(adjusted_timestamp)

        date_formatee = date_object_utc.strftime('%Y-%m-%d %H:%M:%S')

        start_time = convert_ts_human_to_utc(date_formatee)
        start_time = convert_utc_human_to_timezone(start_time, timezone_offset)

        # Ajout des valeurs à la data_list du rapport
        data_list.append(('Date', start_time))
        data_list.append(('Active Calories', active_calories))
        data_list.append(('Total Calories', total_calories))
        logdevinfo(f"Date: {start_time}")
        logdevinfo(f"Active Calories: {active_calories}")
        logdevinfo(f"Total Calories: {total_calories}")


    # Génération du rapport
    report = ArtifactHtmlReport('Garmin_Calories')
    report.start_artifact_report(report_folder, 'Garmin_Calories')
    report.add_script()
    data_headers = ('Key', 'Values')
    report.write_artifact_data_table(data_headers, data_list, file_found)
    report.end_artifact_report()

    # Génère le fichier TSV
    tsvname = 'Garmin_Calories'
    tsv(report_folder, data_headers, data_list, tsvname)

    #insérer les enregistrements horodatés dans la timeline
    #(c’est la première colonne du tableau qui sera utilisée pour horodater l’événement)
    tlactivity = 'Garmin_Calories'
    timeline(report_folder, tlactivity, data_list, data_headers)

