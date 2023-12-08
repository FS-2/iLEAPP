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
import pathlib


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

    users = []
    data_list = []
    # Conversion des éléments en string
    for file_found in files_found:
        file_found = str(file_found)

        # Ouverture et chargement du fichier
        with open(file_found, "rb") as file:
            plist_data = plistlib.load(file)
            path = pathlib.Path(file_found)

            content = resolve_uids(plist_data, plist_data['$objects'])
            root = content['$top']['root']  # Accéder à la racine

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

                formatted_date = date_object_utc.strftime('%Y-%m-%d %H:%M:%S')
                start_time = convert_ts_human_to_utc(formatted_date)
                start_time = convert_utc_human_to_timezone(start_time, timezone_offset)


                user1 = {
                    "Date": start_time,
                    "Gender": gender,
                    "Weight": weight,
                    "Height": height,
                    "Age": age,
                    "lastDeviceUsed": lastDeviceUsed,
                    "UserID": userID,
                    "Path" : path
                }
                users.append(user1)
            except Exception as e:
                pass

            try:
                # Accéder à 'valueKey' dans le dictionnaire 'root'
                value_key = root['valueKey']['userInfo']

                dictionary = {}
                for var in root['valueKey']:
                    if var == "userId":
                        dictionary[var] = root['valueKey'][var]
                for activite in value_key:
                    if activite == 'fullName':
                        dictionary[activite] = value_key[activite]
                    if activite == 'location':
                        dictionary[activite] = value_key[activite]
                dictionary["Path"] = path
                data_list.append(dictionary)

            except Exception as e:
                pass

    final_list = []
    for i in users:
        for j in data_list:
            merged_dictionary = {}
            if i['UserID'] == j['userId']:
                merged_dictionary = {**i, **j}
                if 'userId' in merged_dictionary:
                    del merged_dictionary['userId']
                if "path" in merged_dictionary:
                    del merged_dictionary['path']
                if 'Path' in merged_dictionary:
                    del merged_dictionary['Path']

                final_list.append(merged_dictionary)

    # Génération du rapport
    report = ArtifactHtmlReport('Garmin Profile')
    description = ("User profile information.\n"
                   "The first table contains physical characteristics and the second table contains the full name and location configured by the user. The last table merges the data from the two tables based on the userID.\n"
                   "Please note that data for several userIDs (user profile, subscriber profiles, viewed profiles) are collected."
                   )
    report.start_artifact_report(report_folder, 'Garmin_Profile', description)
    report.add_script()
    data_headers_1 = ('Date', 'Gender', 'Weight [Kg]', 'Size [cm]', 'Age', 'Last used device name', 'UserID', 'Source File Location')
    report.write_artifact_data_table(data_headers_1, [list(i.values()) for i in users], "See Source File Location column", write_total=False)

    data_headers_2 = ('UserID', 'Location', 'Full name', 'Path')
    report.write_artifact_data_table(data_headers_2, [list(i.values()) for i in data_list], 'See Source File Location column',write_total=False)

    date_headers_3 = ('Date', 'Gender', 'Weight [Kg]', 'Size [cm]', 'Age', 'Last used device name', 'UserID', 'Location', 'Full name')
    report.write_artifact_data_table(date_headers_3, [list(i.values()) for i in final_list], 'Link based on userID',write_total=False)
    report.end_artifact_report()

    # Génère le fichier TSV
    tsvname = 'Garmin_profile'
    tsv(report_folder, data_headers_1, [list(i.values()) for i in users], tsvname)
    tsv(report_folder, data_headers_2, [list(i.values()) for i in data_list], tsvname)
    tsv(report_folder, date_headers_3, [list(i.values()) for i in final_list], tsvname)

    # insérer les enregistrements horodatés dans la timeline
    # (c’est la première colonne du tableau qui sera utilisée pour horodater l’événement)
    tlactivity = 'Garmin_profile'
    timeline(report_folder, tlactivity, [list(i.values()) for i in users], data_headers_1)
    timeline(report_folder, tlactivity, [list(i.values()) for i in data_list], data_headers_2)
    timeline(report_folder, tlactivity, [list(i.values()) for i in final_list], date_headers_3)

