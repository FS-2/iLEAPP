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
            #peut avoir plusieurs paths car tuple




import plistlib
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, convert_ts_human_to_utc, convert_utc_human_to_timezone, logdevinfo
import pytz
from datetime import datetime
from scripts.ilapfuncs import tsv
from scripts.ilapfuncs import timeline

#on définit la fonction get_garmin
#paramètres sont utilisés pour traiter des fichiers, générer des rapports,
#rechercher des informations, gérer le formatage du texte et ajuster les décalages de fuseau horaire

def get_garmin_floors(files_found, report_folder, seeker, wrap_text, timezone_offset):
    #Cette liste sera utilisée pour stocker les données extraites
    data_list = []
    #pour chaque élément de la liste files_found, le code convertit l'élément en string

    for file_found in files_found:
            file_found = str(file_found)
        #ouvre le fichier indiqué par file_found en mode binaire (indiqué par "rb") pour la lecture.
        #Le fichier est référencé par la variable fp dans le bloc suivant

            with open(file_found, "rb") as file:

                contenu = plistlib.load(file)
                # si la clé recherchée est trouvée dans le plist (mettre la clé plist pertinente)

                root = contenu['$top']['root']
                object = contenu['$objects']

                # Extraire la dateKey et la valueKey du noeud racine
                date_key = object[root]['dateKey']
                value_key = object[root]['valueKey']

                # Obtention de la valeur associée à dateKey
                date_value = object[date_key]['NS.time']

                # Obtention des informations sur les étages
                floors_dat = object[value_key]

                # Extraire les clés pour les étages descendus et montés
                floors_descended_key = floors_dat['floorsDescendedKey']
                floors_climbed_key = floors_dat['floorsClimbedKey']

                # Obtention des valeurs associées aux clés des étages
                floors_descended = object[floors_descended_key]
                floors_climbed = object[floors_climbed_key]

                epoch_offset = datetime(2001, 1, 1).timestamp()
                adjusted_timestamp = date_value + epoch_offset

                # Convertir le timestamp en objet datetime
                date_object_utc = datetime.utcfromtimestamp(adjusted_timestamp)

                # Appliquer le fuseau horaire (par exemple, UTC+1)
                fuseau_horaire = pytz.timezone('Europe/Paris')  # Remplacez 'Europe/Paris' par votre fuseau horaire
                fuseau_horaire = pytz.timezone('Europe/Paris')
                date_objec = date_object_utc.replace(tzinfo=pytz.utc).astimezone(fuseau_horaire)

                # Formater la date au format demandé
                date_formatte = date_objec.strftime('%d.%m.%Y %H:%M:%S')

                data_list.append(('Date', date_formatte))
                data_list.append(('Floors_climbed', floors_climbed))
                data_list.append(('Floors_descended', floors_descended))


    reports = ArtifactHtmlReport('Garmin_floors')
    # le report folder est définit dans l'interface graphique de iLEAPP
    reports.start_artifact_report(report_folder, 'Garmin_floors')
    reports.add_script()
    data_headers = ('Keys', 'Value')
    reports.write_artifact_data_table(data_headers, data_list, file_found)

    # génère le fichier TSV
    tsvname = 'Garmin_floors'
    tsv(report_folder, data_headers, data_list, tsvname)

    # insérer les enregistrements horodatés dans la timeline
    # (c’est la première colonne du tableau qui sera utilisée pour horodater l’événement)
    tlactivity = 'Garmin_floors'
    timeline(report_folder, tlactivity, data_list, data_headers)

    reports.end_artifact_report()