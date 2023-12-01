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
import matplotlib.pyplot as plt
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


def get_garmin_hearth(files_found, report_folder, seeker, wrap_text, timezone_offset):
    # Liste utilisée pour stocker les données extraites
    data_list = []
    # Conversion des éléments en string
    for file_found in files_found:
            file_found = str(file_found)

            # Ouverture et chargement du fichier plist
            with open(file_found, "rb") as file:
                liste = []
                plist_data = plistlib.load(file)

                contenu = resolve_uids(plist_data, plist_data['$objects'])


                root = contenu['$top']['root']  # Accéder à la racine
                value_key = root['allDayHeartRateKey']['heartRateValues']['NS.objects']

                # Accéder à 'valueKey' dans le dictionnaire 'root'
                for i in value_key:
                    date = i['NS.objects'][0]/1000
                    date = datetime.utcfromtimestamp(date)
                    liste.append((date ,i['NS.objects'][1]))
                dates = [item[0] for item in liste]
                values = [item[1] for item in liste]

                # Créez le graphique
                plt.figure(figsize=(10, 6))
                plt.plot(dates, values, marker='o', linestyle='-')
                plt.title('Graphique de fréquence cardiaque Garmin')
                plt.xlabel('Date')
                plt.ylabel('Fréquence cardiaque')
                plt.grid(True)

                # Générer le HTML pour afficher l'image encodée en base64

                graph_image_path = os.path.join(report_folder, 'garmin_hearth_graph.png')
                plt.savefig(graph_image_path)
                plt.close()

                with open(graph_image_path, "rb") as image_file:
                    graph_image_base64 = base64.b64encode(image_file.read()).decode()

                # Générer le HTML pour afficher l'image encodée en base64
                    img_html = f'<img src="data:image/png;base64,{graph_image_base64}" alt="Garmin Pay Image" style="width:35%;height:auto;">'

                # Ajout des valeurs à la data_list du rapport
                data_list.append(('Image de la carte', img_html))
                logdevinfo(f"'Image de la carte': {img_html}")

    # Génération du rapport
    reports = ArtifactHtmlReport('Garmin_Hearth')
    reports.start_artifact_report(report_folder, 'Garmin_Hearth')
    reports.add_script()
    data_headers = ('Keys', 'Value')
    reports.write_artifact_data_table(data_headers, liste, file_found)
    reports.write_artifact_data_table(data_headers, data_list, file_found)

    # Génère le fichier TSV
    tsvname = 'Garmin_Hearth'
    tsv(report_folder, data_headers, liste, tsvname)

    # insérer les enregistrements horodatés dans la timeline
    # (c’est la première colonne du tableau qui sera utilisée pour horodater l’événement)
    tlactivity = 'Garmin_Hearth'
    timeline(report_folder, tlactivity, liste, data_headers)























