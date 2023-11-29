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

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, convert_ts_human_to_utc, convert_utc_human_to_timezone, logdevinfo

#on définit la fonction get_garmin
#paramètres sont utilisés pour traiter des fichiers, générer des rapports,
#rechercher des informations, gérer le formatage du texte et ajuster les décalages de fuseau horaire
def get_garmin(files_found, report_folder, seeker, wrap_text, timezone_offset):
    #Cette liste sera utilisée pour stocker les données extraites
    data_list = []
    #pour chaque élément de la liste files_found, le code convertit l'élément en string
    for file_found in files_found:
        file_found = str(file_found)
        #ouvre le fichier indiqué par file_found en mode binaire (indiqué par "rb") pour la lecture.
        #Le fichier est référencé par la variable fp dans le bloc suivant
        with open(file_found, "rb") as fp:
            #charge le contenu du fichier ouvert (plist) et stocke le contenu dans la variable plist.
            plist = plistlib.load(fp)
            # si la clé recherchée est trouvée dans le plist (mettre la clé plist pertinente)
            if 'CachedData<RealTimeCalorieData>' in plist:
                #la valeur est la valeur correspondante à la seconde clé recherchée
                val = (plist['dateKey'])
                # enregistre ces informations à l'aide des fonctions logfunc et logdevinfo (fonctions personnalisées pour iLEAPP)
                # ça va enregistrer :  "texte_prédéfini": valeur
                logfunc(f"Date: {val}")
                logdevinfo(f"Date: {val}")
            else:
                logfunc("pas trouvé")

    #génère le rapport HTML
    report = ArtifactHtmlReport('Garmin')
    #le report folder est définit dans l'interface graphique de iLEAPP
    report.start_artifact_report(report_folder, 'Garmin')
    report.add_script()
    data_headers = ('Key', 'Values')
    report.write_artifact_data_table(data_headers, data_list, file_found)
    report.end_artifact_report()

    #génère le fichier TSV
    tsvname = 'Garmin'
    tsv(report_folder, data_headers, data_list, tsvname)

    #insérer les enregistrements horodatés dans la timeline
    #(c’est la première colonne du tableau qui sera utilisée pour horodater l’événement)
    tlactivity = 'Garmin'
    timeline(report_folder, tlactivity, data_list, data_headers)

