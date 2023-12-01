# Module Description: Parses Garmin Connect details
# Author: Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber
# Date: 05.12.2023

__artifacts_v2__ = {
    "Garmin_Connect_Hearth": {
        "name": "Garmin Floors",
        "description": "Extract information of Garmin Connect application",
        "author": "Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber",
        "version": "1.0",
        "date": "2023-12-05",
        "requirements": "none",
        "category": "Application",
        "notes": "",
        "paths": ('*/private/var/mobile/Containers/Data/Application/*/Library/Caches/com.pinterest.PINDiskCache.PINCacheShared/MyDaySeverDataHelper%2EallDayTimeline'),
        "function": "get_garmin_hearth"

    }
}

import plistlib
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, convert_ts_human_to_utc, convert_utc_human_to_timezone, logdevinfo
import pytz
from datetime import datetime
from scripts.ilapfuncs import tsv
from scripts.ilapfuncs import timeline

def get_garmin_hearth(files_found, report_folder, seeker, wrap_text, timezone_offset):
    # Liste utilisée pour stocker les données extraites
    data_list = []
    # Conversion des éléments en string
    for file_found in files_found:
            file_found = str(file_found)

            # Ouverture et chargement du fichier plist
            with open(file_found, "rb") as file:
                contenu = plistlib.load(file)

                # Recherche des valeurs avec les clés associées
                root = contenu['$top']['root']
                objects = contenu['$objects']

                # Valeurs associées aux rythme cardique
                allDayHeartRateKey_UID = objects[root]['allDayHeartRateKey']
                hearth_data = objects[allDayHeartRateKey_UID]
                heartRateValues_UID = hearth_data['heartRateValues']
                NS_data = objects[heartRateValues_UID]
                NS_objects_1 = NS_data['NS.object']
                valeur_UID = NS_objects_1[0]
                NS_data_2 = objects[valeur_UID]
                NS_objects_2 = NS_data_2['NS.objects']
                valeur_UID_2 = NS_objects_2[1]
                battement = objects[valeur_UID_2]

                # Ajout des valeurs à la data_list du rapport
                data_list.append(('Floors_descended', battement))
                logdevinfo(f"floors_descended: {battement}")


    # Génération du rapport
    reports = ArtifactHtmlReport('Garmin_Hearth')
    reports.start_artifact_report(report_folder, 'Garmin_Hearth')
    reports.add_script()
    data_headers = ('Keys', 'Value')
    reports.write_artifact_data_table(data_headers, data_list, file_found)
    reports.end_artifact_report()

    # Génère le fichier TSV
    tsvname = 'Garmin_Hearth'
    tsv(report_folder, data_headers, data_list, tsvname)

    # insérer les enregistrements horodatés dans la timeline
    # (c’est la première colonne du tableau qui sera utilisée pour horodater l’événement)
    tlactivity = 'Garmin_Hearth'
    timeline(report_folder, tlactivity, data_list, data_headers)