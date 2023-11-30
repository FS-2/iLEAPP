# Module Description: Parses Garmin Connect details
# Author: Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber
# Date: 05.12.2023

__artifacts_v2__ = {
    "Garmin_Connect_Pay": {
        "name": "Garmin Pay",
        "description": "Extract information of Garmin Connect application",
        "author": "Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber",
        "version": "1.0",
        "date": "2023-12-05",
        "requirements": "none",
        "category": "Application",
        "notes": "",
        "paths": ('*/private/var/mobile/Containers/Data/Application/*/Library/Caches/GarminPayImageCache/*'),
        "function": "get_garmin_pay"

    }
}

import plistlib
import json
import base64
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, convert_ts_human_to_utc, convert_utc_human_to_timezone, logdevinfo
import pytz
from datetime import datetime
from scripts.ilapfuncs import tsv
from scripts.ilapfuncs import timeline

def get_garmin_pay(files_found, report_folder, seeker, wrap_text, timezone_offset):
    # Liste utilisée pour stocker les données extraites
    data_list = []

        # Pour le premier fichier (PNG)
        if file_found == files_found[0]:

            # Ouverture et chargement du fichier
            img_html = f'<img src="file://{file_found}" alt="Garmin Pay Image" style="width:100%;height:auto;">'

            # Ajout des valeurs à la data_list du rapport
            data_list.append(('Image de la carte', img_html))
            logdevinfo(f"'Image de la carte': {img_html}")



    # Génération du rapport
    reports = ArtifactHtmlReport('Garmin_Pay')
    reports.start_artifact_report(report_folder, 'Garmin_Pay')
    reports.add_script()
    data_headers = ('Keys', 'Value')
    reports.write_artifact_data_table(data_headers, data_list, file_found)
    reports.end_artifact_report()

    # Génère le fichier TSV
    tsvname = 'Garmin_Pay'
    tsv(report_folder, data_headers, data_list, tsvname)

    # insérer les enregistrements horodatés dans la timeline
    # (c’est la première colonne du tableau qui sera utilisée pour horodater l’événement)
    tlactivity = 'Garmin_Pay'
    timeline(report_folder, tlactivity, data_list, data_headers)