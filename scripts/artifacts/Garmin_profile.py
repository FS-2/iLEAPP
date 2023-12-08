# Module Description: Get information related to user profile
# Author: Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber
# Date: 08.12.2023

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

#Function to simplify data storage (resolve UIDs)
def resolve_uids(item, objects):

    if isinstance(item, plistlib.UID):
        return resolve_uids(objects[item.data], objects)
    elif isinstance(item, dict):
        return {key: resolve_uids(value, objects) for key, value in item.items()}
    elif isinstance(item, list):
        return [resolve_uids(value, objects) for value in item]
    else:
        return item

def get_garmin_profile(files_found, report_folder, seeker, wrap_text, timezone_offset):
    # Create an empty list to store extracted data
    users = []
    data_list = []
    # Convert elements to string
    for file_found in files_found:
        file_found = str(file_found)

        # Opening and loading the file
        with open(file_found, "rb") as file:
            plist_data = plistlib.load(file)

            path = pathlib.Path(file_found) # File path

            content = resolve_uids(plist_data, plist_data['$objects']) # Simplify data storage format
            root = content['$top']['root'] # Go to root

            try:
                date = root['dateKey']['NS.time']

                # Accesses 'valueKey' in the 'root' dictionary
                value_key = root['valueKey']

                # Now accesses 'biometricProfile' under 'valueKey'.
                biometric_profile = value_key['biometricProfile']

                # Retrieve 'biometricProfile' data
                gender = biometric_profile['gender']
                weight = biometric_profile['weight']
                height = biometric_profile['height']
                age = biometric_profile['age']
                # Formats weight
                weight = weight/1000

                last_device = value_key['lastUsedDevice']
                lastDeviceUsed = last_device['lastUsedDeviceName']
                userID = last_device['userProfileNumber']

                # Date format conversion
                epoch_offset = datetime(2001, 1, 1).timestamp()
                adjusted_timestamp = date + epoch_offset
                date_object_utc = datetime.utcfromtimestamp(adjusted_timestamp)

                formatted_date = date_object_utc.strftime('%Y-%m-%d %H:%M:%S')
                start_time = convert_ts_human_to_utc(formatted_date)
                start_time = convert_utc_human_to_timezone(start_time, timezone_offset)

                # Create a dictionary for each profile_biometric
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

                # Each profile is added to a list
                users.append(user1)

            except Exception as e:
                pass

            try:
                # Access 'valueKey' in the 'root' dictionary
                value_key = root['valueKey']['userInfo']

                dictionary = {}
                # Retrieves profile information
                for var in root['valueKey']:
                    if var == "userId":
                        dictionary[var] = root['valueKey'][var]
                for activite in value_key:
                    if activite == 'fullName':
                        dictionary[activite] = value_key[activite]
                    if activite == 'location':
                        dictionary[activite] = value_key[activite]
                dictionary["Path"] = path
                # Adds each profile to data_list
                data_list.append(dictionary)

            except Exception as e:
                pass

    # Links data_list and users if they have the same userID to create a 3rd table
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

    # Generates report
    # 3 tables in all: one for biometrics, one for profile and one that links the two.
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

    # Generates TSV file
    tsvname = 'Garmin_Profile'
    tsv(report_folder, data_headers_1, [list(i.values()) for i in users], tsvname)
    tsv(report_folder, data_headers_2, [list(i.values()) for i in data_list], tsvname)
    tsv(report_folder, date_headers_3, [list(i.values()) for i in final_list], tsvname)

    # Insert time-stamped records in timeline
    # (the first column of the table will be used to time-stamp the event)
    # The second table (with headers_2) is not inserted in timeline, as it contains no time-stamped records
    tlactivity = 'Garmin_Profile'
    timeline(report_folder, tlactivity, [list(i.values()) for i in users], data_headers_1)
    timeline(report_folder, tlactivity, [list(i.values()) for i in final_list], date_headers_3)

