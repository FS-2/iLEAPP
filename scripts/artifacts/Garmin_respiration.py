# Module Description: Parses Garmin Connect details
# Author: Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber
# Date: 05.12.2023

__artifacts_v2__ = {
    "Garmin_Connect_respiration": {
        "name": "Garmin respiration",
        "description": "Extract information of Garmin Connect application",
        "author": "Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber",
        "version": "1.0",
        "date": "2023-12-05",
        "requirements": "none",
        "category": "Garmin Application",
        "notes": "",
        "paths": ('*/private/var/mobile/Containers/Data/Application/*/Library/Caches/com.pinterest.PINDiskCache.PINCacheShared/MyDaySeverDataHelper%2EallDayTimeline'),
        "function": "get_garmin_respiration"
    }
}

import plistlib
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, convert_ts_human_to_utc, convert_utc_human_to_timezone, logdevinfo
import pytz
from datetime import datetime, timezone
from scripts.ilapfuncs import tsv
from scripts.ilapfuncs import timeline
import plotly.graph_objects as go
import base64
import os

def resolve_uids(item, objects):
    """
    Fonction récursive pour résoudre les références UID dans les données plist.
    """
    if isinstance(item, plistlib.UID):
        # Résoudre la référence UID
        return resolve_uids(objects[item.data], objects)
    elif isinstance(item, dict):
        # Résoudre récursivement dans les dictionnaires
        return {key: resolve_uids(value, objects) for key, value in item.items()}
    elif isinstance(item, list):
        # Résoudre récursivement dans les listes
        return [resolve_uids(value, objects) for value in item]
    else:
        # Retourner l'item tel quel s'il ne s'agit ni d'un UID, ni d'un dictionnaire, ni d'une liste
        return item


def get_garmin_respiration(files_found, report_folder, seeker, wrap_text, timezone_offset):
    # Liste utilisée pour stocker les données extraites

    # Conversion des éléments en string
    for file_found in files_found:
        file_found = str(file_found)

        # Ouverture et chargement du fichier plist
        with open(file_found, "rb") as file:
            list = []
            plist_data = plistlib.load(file)

            content = resolve_uids(plist_data, plist_data['$objects'])
            root = content['$top']['root']  # Accéder à la racine
            value_key = root['allDayRespirationKey']['respirationValuesArray']['NS.objects']
            value_user = root['allDayRespirationKey']

            # Accède à 'valueKey' dans le dictionnaire 'root'
            for i in value_key:
                date = i['startTimeGMT']
                utc_datetime = datetime.fromtimestamp(date, timezone.utc)

                formatted_date = utc_datetime.strftime('%Y-%m-%d %H:%M:%S')

                start_time = convert_ts_human_to_utc(formatted_date)
                start_time = convert_utc_human_to_timezone(start_time, timezone_offset)
                list.append((start_time, i['value'],value_user['userProfilePK']))

            dates = [item[0] for item in list]
            values = [item[1] for item in list]

            # Crée le graphique
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=dates, y=values, mode='lines+markers', name='Fréquence cardiaque'))

            # Mise en page
            fig.update_layout(title='Garmin Respiration Rate Graph',
                                xaxis_title='Date',
                                yaxis_title='Respiration',
                                template='plotly_white')

            # Enregistre le graphique sous forme d'image PNG
            graph_image_path = os.path.join(report_folder, 'garmin_respiration_graph.png')
            fig.write_image(graph_image_path)

            # Ouvre l'image
            with open(graph_image_path, "rb") as image_file:
                data_list = []
                graph_image_base64 = base64.b64encode(image_file.read()).decode()

                # Générer le HTML pour afficher l'image encodée en base64
                img_html = f'<img src="data:image/png;base64,{graph_image_base64}" alt="Garmin Respiration Graph" style="width:65%;height:auto;">'

                # Ajout des valeurs à la data_list du rapport
                data_list.append(('Respiration Rate Graph', img_html))

    # Génération du rapport
    report = ArtifactHtmlReport('Garmin Respiration')
    description = 'Respiration rate on last day (measured every two minutes)'
    report.start_artifact_report(report_folder, 'Garmin_Respiration', description)
    report.add_script()
    data_headers_1 = ('Date', 'Respiration Rate', 'userid')
    report.write_artifact_data_table(data_headers_1, list, file_found)
    data_headers_2 = ('Description', 'Graph')
    report.write_artifact_data_table(data_headers_2, data_list, file_found, html_escape=False)
    report.end_artifact_report()

    # Génère le fichier TSV
    tsvname = 'Garmin_Respiration'
    tsv(report_folder, data_headers_1, list, tsvname)
    #tsv(report_folder, data_headers_1, data_list, tsvname)

    # insérer les enregistrements horodatés dans la timeline
    # (c’est la première colonne du tableau qui sera utilisée pour horodater l’événement)
    tlactivity = 'Garmin_Respiration'
    timeline(report_folder, tlactivity, list, data_headers_1)
    #timeline(report_folder, tlactivity, data_list, data_headers_1)
