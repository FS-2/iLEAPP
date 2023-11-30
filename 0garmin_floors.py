# Module Description: Parses Garmin Connect details
# Author: Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber
# Date: 05.12.2023

__artifacts_v2__ = {
    "Garmin_Connect_Floors": {
        "name": "Garmin Connect Floors",
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

#on définit la fonction get_garmin
#paramètres sont utilisés pour traiter des fichiers, générer des rapports,
#rechercher des informations, gérer le formatage du texte et ajuster les décalages de fuseau horaire
def get_garmin_floors(files_found, report_folder, seeker, wrap_text, timezone_offset):
    #Cette liste sera utilisée pour stocker les données extraites
    data_list = []
    #pour chaque élément de la liste files_found, le code convertit l'élément en string
    file_found = str(files_found)

    # ouvre le fichier indiqué par file_found en mode binaire (indiqué par "rb") pour la lecture.
    with open(file_found, "rb") as fp:
        # charge le contenu du fichier ouvert (plist) et stocke le contenu dans la variable pl.
        contenu = plistlib.load(fp)
        root = contenu['$top']['root']
        objects = contenu['$objects']
        value_key = objects[root]['valueKey']
        floor_data = objects[value_key]
        # Accès aux données spécifiques à RealTimeCalorieData
        floors_Descended_Key = floor_data['floorsDescendedKey']
        floors_Climbed_Key = floor_data['floorsClimbedKey']

        # Obtention des valeurs associées aux clés des calories
        floors_descended = objects[floors_Descended_Key]
        floors_climbed = objects[floors_Climbed_Key]

        data_list.append(('floors_descended', floors_descended))
        data_list.append(('floors_climbed', floors_climbed))
        logdevinfo(f"floors_descended: {floors_descended}")
        logdevinfo(f"floors_climbed: {floors_climbed}")


    #génère le rapport HTML
    report = ArtifactHtmlReport('Garmin_Floors')
    #le report folder est définit dans l'interface graphique de iLEAPP
    report.start_artifact_report(report_folder, 'Garmin_Floors')
    report.add_script()
    data_headers = ('Key', 'Values')
    report.write_artifact_data_table(data_headers, data_list, file_found)
    report.end_artifact_report()

    #génère le fichier TSV
    tsvname = 'Garmin_Floors'
    tsv(report_folder, data_headers, data_list, tsvname)

    #insérer les enregistrements horodatés dans la timeline
    #(c’est la première colonne du tableau qui sera utilisée pour horodater l’événement)
    tlactivity = 'Garmin_Floors'
    timeline(report_folder, tlactivity, data_list, data_headers)