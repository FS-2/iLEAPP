# Module Description: Parses Garmin Connect details
# Author: Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber
# Date: 05.12.2023

__artifacts_v2__ = {
    "Garmin_Connect_Floors": {
        "name": "Garmin Floors",
        "description": "Extract information of Garmin Connect application",
        "author": "Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber",
        "version": "1.0",
        "date": "2023-12-05",
        "requirements": "none",
        "category": "Application",
        "notes": "",
        "paths": ('*/private/var/mobile/Containers/Data/Application/*/Library/Caches/com.pinterest.PINDiskCache.PINCacheShared/MyDayRealTimeDataService_realTimeFloorsCacheDataKey'),
        "function": "get_garmin_floors"

    }
}

import plistlib
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, convert_ts_human_to_utc, convert_utc_human_to_timezone, logdevinfo
import pytz
from datetime import datetime
from scripts.ilapfuncs import tsv
from scripts.ilapfuncs import timeline

def get_garmin_floors(files_found, report_folder, seeker, wrap_text, timezone_offset):
    # Liste utilisée pour stocker les données extraites
    data_list = []
    # Conversion des éléments en string
    for file_found in files_found:
            file_found = str(file_found)

            # Ouverture et chargement du fichier
            with open(file_found, "rb") as file:
                contenu = plistlib.load(file)

                # Recherche des valeurs avec les clés associées
                root = contenu['$top']['root']
                objects = contenu['$objects']

                # Valeurs associées aux étages
                value_key = objects[root]['valueKey']
                floors_data = objects[value_key]
                floors_descended_key = floors_data['floorsDescendedKey']
                floors_climbed_key = floors_data['floorsClimbedKey']
                floors_descended = objects[floors_descended_key]
                floors_climbed = objects[floors_climbed_key]

                # Valeurs associées à la date
                date_key = objects[root]['dateKey']
                date_value = objects[date_key]['NS.time']

                # Conversion du format de la date
                epoch_offset = datetime(2001, 1, 1).timestamp()
                adjusted_timestamp = date_value + epoch_offset
                date_object_utc = datetime.utcfromtimestamp(adjusted_timestamp)

                date_formatee = date_object_utc.strftime('%Y-%m-%d %H:%M:%S')
                start_time = convert_ts_human_to_utc(date_formatee)
                start_time = convert_utc_human_to_timezone(start_time, timezone_offset)

                # Ajout des valeurs à la data_list du rapport
                data_list.append(('Date', start_time))
                data_list.append(('Floors_climbed', floors_climbed))
                data_list.append(('Floors_descended', floors_descended))
                


    # Génération du rapport
    reports = ArtifactHtmlReport('Garmin_floors')
    reports.start_artifact_report(report_folder, 'Garmin_floors')
    reports.add_script()
    data_headers = ('Keys', 'Value')
    reports.write_artifact_data_table(data_headers, data_list, file_found)
    reports.end_artifact_report()

    # Génère le fichier TSV
    tsvname = 'Garmin_floors'
    tsv(report_folder, data_headers, data_list, tsvname)

    # insérer les enregistrements horodatés dans la timeline
    # (c’est la première colonne du tableau qui sera utilisée pour horodater l’événement)
    tlactivity = 'Garmin_floors'
    timeline(report_folder, tlactivity, data_list, data_headers)