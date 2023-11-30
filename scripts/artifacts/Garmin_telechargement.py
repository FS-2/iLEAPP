# Module Description: Parses Garmin Connect details
# Author: Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber
# Date: 05.12.2023

__artifacts_v2__ = {
    "Garmin_Connect_Telechargement": {
        "name": "Garmin Telechargement",
        "description": "Extract information of Garmin Connect application",
        "author": "Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber",
        "version": "1.0",
        "date": "2023-12-05",
        "requirements": "none",
        "category": "Application",
        "notes": "",
        "paths": ('*/private/var/containers/Bundle/Application/*/iTunesMetadata.plist', '*/private/var/mobile/Containers/Data/Application/*/Library/Caches/com.crashlytics.data/com.garmin.connect.mobile/v5/settings/cache-key.json'),
        "function": "get_garmin_telechargement"

    }
}

import plistlib
import json
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, convert_ts_human_to_utc, convert_utc_human_to_timezone, logdevinfo
import pytz
from datetime import datetime
from scripts.ilapfuncs import tsv
from scripts.ilapfuncs import timeline

def get_garmin_telechargement(files_found, report_folder, seeker, wrap_text, timezone_offset):
    # Liste utilisée pour stocker les données extraites
    data_list = []
    # Conversion des éléments en string
    for file_found in files_found:
            file_found = str(file_found)

            if files_found:
                file_found = files_found[0]

                # Ouverture et chargement du fichier
                with open(file_found, "rb") as file:
                    contenu = plistlib.load(file)

                    # Recherche des valeurs avec les clés associées
                    apple_id = contenu['com.apple.iTunesStore.downloadInfo']['accountInfo']['AppleID']
                    purchaseDate = contenu['com.apple.iTunesStore.downloadInfo']['purchaseDate']

                    # Formatage de la date
                    date_object = datetime.fromisoformat(purchaseDate)
                    date_formatee = date_object.strftime('%d.%m.%Y %H:%M:%S')

                    # Ajout des valeurs à la data_list du rapport
                    data_list.append(('Apple_id', apple_id))
                    data_list.append(('Date de téléchargement de l’application', date_formatee))
                    logdevinfo(f"'Apple_id': {apple_id}")
                    logdevinfo(f"'Date de téléchargement de l’application': {date_formatee}")

            if files_found:
                file_found = files_found[1]
                with open(file_found, 'r') as file:
                    contenu = json.load(file)

                    # Recherche des valeurs avec les clés associées
                    app_version = contenu['app_version']
                    google_app_id = contenu['google_app_id']

                    # Ajout des valeurs à la data_list du rapport
                    data_list.append(('App version', app_version))
                    data_list.append(('App ID', google_app_id))
                    logdevinfo(f"'App version': {app_version}")
                    logdevinfo(f"'App ID': {google_app_id}")



    # Génération du rapport
    reports = ArtifactHtmlReport('Garmin_Telechargement')
    reports.start_artifact_report(report_folder, 'Garmin_Telechargement')
    reports.add_script()
    data_headers = ('Keys', 'Value')
    reports.write_artifact_data_table(data_headers, data_list, file_found)
    reports.end_artifact_report()

    # Génère le fichier TSV
    tsvname = 'Garmin_Telechargement'
    tsv(report_folder, data_headers, data_list, tsvname)

    # insérer les enregistrements horodatés dans la timeline
    # (c’est la première colonne du tableau qui sera utilisée pour horodater l’événement)
    tlactivity = 'Garmin_Telechargement'
    timeline(report_folder, tlactivity, data_list, data_headers)