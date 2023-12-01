# Module Description: Parses Garmin Connect details
# Author: Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber
# Date: 05.12.2023

__artifacts_v2__ = {
    "Garmin_Connect_5": {
        "name": "Garmin_profile2",
        "description": "Extract information of Garmin Connect application",
        "author": "Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber",
        "version": "1.0",
        "date": "2023-11-30",
        "requirements": "none",
        "category": "Application",
        "notes": "",
        "paths": ('*/private/var/mobile/Containers/Data/Application/*/Caches/com.pinterest.PINDiskCache.PINCacheShared/UserProfile%2EinformationData%*'),
        "function": "get_garmin_profile2"



    }
}
import plistlib
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, convert_ts_human_to_utc, convert_utc_human_to_timezone, logdevinfo
import pytz
from datetime import datetime
from scripts.ilapfuncs import tsv
from scripts.ilapfuncs import timeline






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


def get_garmin_profile2(files_found, report_folder, seeker, wrap_text, timezone_offset):

    # pour chaque élément de la liste files_found, le code convertit l'élément en string
    liste_tuples = []
    for file_found in files_found:
        file_found = str(file_found)
        # ouvre le fichier indiqué par file_found en mode binaire (indiqué par "rb") pour la lecture.
        # Le fichier est référencé par la variable fp dans le bloc suivant

        with open(file_found, "rb") as fp:


            plist_data = plistlib.load(fp)

            contenu = resolve_uids(plist_data, plist_data['$objects'])


            root = contenu['$top']['root']  # Accéder à la racine

            # Accéder à 'valueKey' dans le dictionnaire 'root'
            value_key = root['valueKey']['userInfo']

            dictionnaire = {}
            for var in root['valueKey']:
                if var == "userId":
                    dictionnaire[var] = root['valueKey'][var]
            for activite in value_key:

                if activite == 'fullName':
                    dictionnaire[activite] = value_key[activite]
                if activite == 'location':
                    dictionnaire[activite] = value_key[activite]

            liste_tuples.append(dictionnaire)
            print(liste_tuples)

    reports = ArtifactHtmlReport('Garmin_Profile2')
    reports.start_artifact_report(report_folder, 'Garmin_Profile2')
    reports.add_script()
    data_headers = ('UserID', 'Localisation', 'Nom complet')

    reports.write_artifact_data_table(data_headers, [list(i.values()) for i in liste_tuples], file_found,write_total=False)

    reports.end_artifact_report()

    # Génère le fichier TSV
    tsvname = 'Garmin_Profile2'
    tsv(report_folder, data_headers, [list(i.values()) for i in liste_tuples], tsvname)

    # insérer les enregistrements horodatés dans la timeline
    # (c’est la première colonne du tableau qui sera utilisée pour horodater l’événement)
    tlactivity = 'Garmin_Profile2'
    timeline(report_folder, tlactivity, [list(i.values()) for i in liste_tuples], data_headers)