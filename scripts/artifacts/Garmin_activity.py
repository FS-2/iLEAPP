# Module Description: Parses Garmin Connect details
# Author: Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber
# Date: 05.12.2023

__artifacts_v2__ = {
    "Garmin_Connect_Activity": {
        "name": "Garmin_Activity",
        "description": "Extract information of Garmin Connect application",
        "author": "Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber",
        "version": "1.0",
        "date": "2023-11-30",
        "requirements": "none",
        "category": "Garmin Application",
        "notes": "",
        "paths": ('*/private/var/mobile/Containers/Data/Application/*/Library/Caches/com.pinterest.PINDiskCache.PINCacheShared/UserProfile%2EsummarizedActivityData%*'),
        "function": "get_garmin_activity"
    }
}
import plistlib
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, convert_ts_human_to_utc, convert_utc_human_to_timezone, logdevinfo
import pytz
from datetime import datetime
from scripts.ilapfuncs import tsv
from scripts.ilapfuncs import timeline
from geopy import *
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
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

def get_garmin_activity(files_found, report_folder, seeker, wrap_text, timezone_offset):

    #empty list to add different activities
    data_list = []
    # for each element in the files_found list, the code converts the element into a string
    for file_found in files_found:
        file_found = str(file_found)

        # opens the file indicated by file_found in binary mode (indicated by "rb") for reading.
        with open(file_found, "rb") as fp:
            plist_data = plistlib.load(fp)
            #We simplify the format
            content = resolve_uids(plist_data, plist_data['$objects'])
            # Go to root
            root = content['$top']['root']

            # Access 'valueKey' in the 'root' dictionary
            value_key = root['valueKey']
            #file path
            path = pathlib.Path(file_found)

            # Now access 'biometricProfile' under 'valueKey'.
            for activity in value_key['NS.objects']:
                dict_activities = {}
                list_loc = []
                # here we'll search for the keys we want to find their value and for some we'll reformat them
                for key in ['startTimeLocal','ownerId','activityName', 'calories', 'distance', 'duration',  'maxHR',
                            'maxSpeed', 'startLongitude', 'startLatitude']:
                    if key in activity['NS.keys']:
                        index = activity['NS.keys'].index(key)
                        dict_activities[key] = activity['NS.objects'][index]  # Ajoutez la valeur au dictionnaire
                        if key == 'distance':
                            dict_activities[key] = activity['NS.objects'][index]/1000
                        if key == 'maxSpeed':
                            dict_activities[key] = activity['NS.objects'][index]*(3.6)
                        if key == 'duration':
                            dict_activities[key] = activity['NS.objects'][index]/60
                        if key =='startLongitude':
                            list_loc.append(activity['NS.objects'][index])
                        if key =='startLatitude':
                            list_loc.append(activity['NS.objects'][index])
                        # here we reformat the date
                        if key == 'startTimeLocal':
                            activity_date_str = activity['NS.objects'][index]
                            if activity_date_str.endswith('.0'):
                                activity_date_str = activity_date_str[:-1] + '+01:00'


                            if '.' in activity_date_str:
                                parts = activity_date_str.split('.')
                                activity_date_str = parts[0] + '.' + parts[1][:6]

                            activity_date = datetime.fromisoformat(activity_date_str)
                            date_timestamp = activity_date.timestamp()
                            date_object_utc = datetime.utcfromtimestamp(date_timestamp)
                            formatted_date = date_object_utc.strftime('%Y-%m-%d %H:%M:%S')
                            start_time = convert_ts_human_to_utc(formatted_date)
                            start_time = convert_utc_human_to_timezone(start_time, timezone_offset)
                            dict_activities[key] = start_time
                    # if the key is not known, the value will be unknown
                    else:
                        dict_activities[key] = 'Unknown'
                # if we have latitude and longitude, we'll look up the address
                if len(list_loc) != 0:
                    try:
                        geolocator = Nominatim(user_agent="geoapiExercises")
                        location = geolocator.reverse((list_loc[1], list_loc[0]))
                        dict_activities["Address"] = location
                    except GeocoderTimedOut as e1:
                        print(f"GeocoderTimedOutError: {e1}")
                        dict_activities["Address"] = 'Unknown'
                    except GeocoderServiceError as e2:
                        print(f"GeocoderServiceError: {e2}")
                        dict_activities["Address"] = 'Unknown'
                else:
                    dict_activities["Address"] = "Unknown"

                dict_activities["Source File Location"] = path

                # add activity to list
                data_list.append(dict_activities)

    # Here we create the HTML report and add our data
    report = ArtifactHtmlReport('Garmin Activity')

    description = "Lists the activities performed by the user of the application, as well as the activities performed by the profiles consulted and the users to which he or she has subscribed"
    report.start_artifact_report(report_folder, 'Garmin_Activity', description)
    report.add_script()
    data_headers = ("Start Date","UserID", "Activity", "Calories", "Distance [km]", "Duration [min]",  "maxHR", "maxSpeed [km/h]", "StartLongitude", "StartLatitude", "Address", "Source File Location")
    report.write_artifact_data_table(data_headers, [list(i.values()) for i in data_list], "See Source File Location column", write_total=False)
    report.end_artifact_report()

    # generates TSV file
    tsvname = 'Garmin_Activity'
    tsv(report_folder, data_headers, [list(i.values()) for i in data_list], tsvname)
    # insert time-stamped records in timeline
    # (the first column of the table will be used to time-stamp the event)
    tlactivity = 'Garmin_Activity'
    timeline(report_folder, tlactivity, [list(i.values()) for i in data_list], data_headers)

