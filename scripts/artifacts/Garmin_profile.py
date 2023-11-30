# Module Description: Parses Garmin Connect details
# Author: Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber
# Date: 05.12.2023

__artifacts_v2__ = {
    "Garmin_Connect_3": {
        "name": "Garmin_profile",
        "description": "Extract information of Garmin Connect application",
        "author": "Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber",
        "version": "1.0",
        "date": "2023-11-30",
        "requirements": "none",
        "category": "Application",
        "notes": "",
        "paths": ('*/private/var/mobile/Containers/Data/Application/*/Library/Caches/com.pinterest.PINDiskCache.PINCacheShared/UserProfile%2EaboutData%*'),
        "function": "get_garmin_profile"

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

def get_garmin_profile(files_found, report_folder, seeker, wrap_text, timezone_offset):
    #Cette liste sera utilisée pour stocker les données extraites
    liste = []
    #pour chaque élément de la liste files_found, le code convertit l'élément en string
    utilisateur = []
    for file_found in files_found:
            file_found = str(file_found)
        #ouvre le fichier indiqué par file_found en mode binaire (indiqué par "rb") pour la lecture.
        #Le fichier est référencé par la variable fp dans le bloc suivant

            with open(file_found, "rb") as file:




                plist_data = plistlib.load(file)


                contenu = resolve_uids(plist_data, plist_data['$objects'])

                root = contenu['$top']['root']  # Accéder à la racine


                date = root['dateKey']['NS.time']


                # Accéder à 'valueKey' dans le dictionnaire 'root'
                value_key = root['valueKey']

                # Maintenant, accédez à 'biometricProfile' sous 'valueKey'
                biometric_profile = value_key['biometricProfile']

                # Récupérer les données de 'biometricProfile'
                gender = biometric_profile['gender']  # 'MALE'
                weight = biometric_profile['weight']  # 75000.0
                height = biometric_profile['height']  # 175.0
                age = biometric_profile['age']  # 22
                activity_level = biometric_profile['activityLevel']  # 0
                vo2_max_running = biometric_profile['vo2MaxRunning']  # 0.0
                weight = weight/1000

                last_device = value_key['lastUsedDevice']
                lastDeviceUsed = last_device['lastUsedDeviceName']
                userID = last_device['userProfileNumber']

                date_convert = convert_ts_human_to_utc(date)
                date_convert = convert_utc_human_to_timezone(date_convert,timezone_offset)
                utilisateur1 = {
                    "Date": date_convert,
                    "Genre": gender,
                    "Poids": weight,
                    "Taille": height,
                    "Age": age,
                    "DernierAppareilUtilisé": lastDeviceUsed,
                    "UserID": userID
                }
                utilisateur.append(utilisateur1)


    reports = ArtifactHtmlReport('Garmin_Profile')
    # le report folder est définit dans l'interface graphique de iLEAPP
    reports.start_artifact_report(report_folder, 'Garmin_Profile')
    reports.add_script()
    data_headers = ('Date', 'Genre', 'Poids [Kg]', 'Taille', 'Age', 'DernierAppareilUtilisé', 'UserID')

    for user in utilisateur:
        reports.write_artifact_data_table(data_headers, [user.values()], file_found, write_total=False)


    # génère le fichier TSV
    tsvname = 'Garmin_Profile'
    tsv(report_folder, data_headers, liste, tsvname)

    # insérer les enregistrements horodatés dans la timeline
    # (c’est la première colonne du tableau qui sera utilisée pour horodater l’événement)
    tlactivity = 'Garmin_Profile'
    timeline(report_folder, tlactivity, liste, data_headers)

    reports.end_artifact_report()





