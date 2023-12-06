# Module Description: Parses Garmin Connect details
# Author: Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber
# Date: 05.12.2023

__artifacts_v2__ = {
    "Garmin_Connect_profile": {
        "name": "Garmin_profile",
        "description": "Extract informatio of Garmin Connect application",
        "author": "Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber",
        "version": "1.0",
        "date": "2023-11-30",
        "requirements": "none",
        "category": "Garmin Application",
        "notes": "",
        "paths": ('*/private/var/mobile/Containers/Data/Application/*/Library/Caches/com.pinterest.PINDiskCache.PINCacheShared/UserProfile%2EaboutData%*','*/private/var/mobile/Containers/Data/Application/*/Caches/com.pinterest.PINDiskCache.PINCacheShared/UserProfile%2EinformationData%*'),

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
    # Liste utilisée pour stocker les données extraites

    utilisateur = []
    liste_tuples=[]
    # Conversion des éléments en string
    reports = ArtifactHtmlReport('Garmin_Profile')
    for file_found in files_found:
            file_found = str(file_found)
            # Ouverture et chargement du fichier
            with open(file_found, "rb") as file:
                plist_data = plistlib.load(file)


                contenu = resolve_uids(plist_data, plist_data['$objects'])

                root = contenu['$top']['root']  # Accéder à la racine

                try:


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

                    epoch_offset = datetime(2001, 1, 1).timestamp()
                    adjusted_timestamp = date + epoch_offset
                    date_object_utc = datetime.utcfromtimestamp(adjusted_timestamp)

                    date_formatee = date_object_utc.strftime('%Y-%m-%d %H:%M:%S')
                    start_time = convert_ts_human_to_utc(date_formatee)
                    start_time = convert_utc_human_to_timezone(start_time, timezone_offset)


                    utilisateur1 = {
                        "Date": start_time,
                        "Genre": gender,
                        "Poids": weight,
                        "Taille": height,
                        "Age": age,
                        "DernierAppareilUtilisé": lastDeviceUsed,
                        "UserID": userID
                    }
                    utilisateur.append(utilisateur1)
                except Exception as e:
                    pass




                try:
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

                except Exception as e:
                    pass


    liste_final = []
    for i in utilisateur:
        for j in liste_tuples:
            dictionnaire_fusion = {}
            if i['UserID'] == j['userId']:
                dictionnaire_fusion = {**i, **j}
                if 'userId' in dictionnaire_fusion:
                    del dictionnaire_fusion['userId']

                liste_final.append(dictionnaire_fusion)



    # Génération du rapport

    reports.start_artifact_report(report_folder, 'Garmin_Profile')
    reports.add_script()
    data_headers = ('Date', 'Genre', 'Poids [Kg]', 'Taille [cm]', 'Age', 'DernierAppareilUtilisé', 'UserID')



    reports.write_artifact_data_table(data_headers, [list(i.values()) for i in utilisateur], file_found, write_total=False)

    data_header = ('UserID', 'Localisation', 'Nom complet')

    reports.write_artifact_data_table(data_header, [list(i.values()) for i in liste_tuples], file_found,write_total=False)

    data_head = ('Date', 'Genre', 'Poids [Kg]', 'Taille [cm]', 'Age', 'DernierAppareilUtilisé', 'UserID', 'Localisation', 'Nom complet')
    reports.write_artifact_data_table(data_head, [list(i.values()) for i in liste_final], file_found,write_total=False)




    # Génère le fichier TSV
    tsvname = 'Garmin_profile'
    tsv(report_folder, data_headers, [list(i.values()) for i in utilisateur], tsvname)

    # insérer les enregistrements horodatés dans la timeline
    # (c’est la première colonne du tableau qui sera utilisée pour horodater l’événement)
    tlactivity = 'Garmin_profile'
    timeline(report_folder, tlactivity, [list(i.values()) for i in utilisateur], data_headers)

