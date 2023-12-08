# Module Description: Parses Garmin Connect details
# Author: Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber
# Date: 05.12.2023

__artifacts_v2__ = {
    "Garmin_Connect_respiration": {
        "name": "Garmin respiration",
        "description": "Extract information of Garmin Connect application",
        "author": "Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber",
        "version": "1.0",
        "date": "2023-12-05",
        "requirements": "none",
        "category": "Garmin Application",
        "notes": "",
        "paths": ('*/private/var/mobile/Containers/Data/Application/*/Library/Caches/com.pinterest.PINDiskCache.PINCacheShared/MyDaySeverDataHelper%2EallDayTimeline'),
        "function": "get_garmin_respiration"
    }
}

import plistlib
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, convert_ts_human_to_utc, convert_utc_human_to_timezone, logdevinfo
import pytz
from datetime import datetime, timezone
from scripts.ilapfuncs import tsv
from scripts.ilapfuncs import timeline
import plotly.graph_objects as go
import base64
import os
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


def get_garmin_respiration(files_found, report_folder, seeker, wrap_text, timezone_offset):
    # Convert elements to string
    for file_found in files_found:
        file_found = str(file_found)

        # Opening and loading the plist file
        with open(file_found, "rb") as file:
            list = []
            plist_data = plistlib.load(file)

            content = resolve_uids(plist_data, plist_data['$objects'])
            root = content['$top']['root']  # Go to root
            value_key = root['allDayRespirationKey']['respirationValuesArray']['NS.objects']
            value_user = root['allDayRespirationKey']

            # Accesses 'valueKey' in the 'root' dictionary
            for i in value_key:
                #access and reformat the date
                date = i['startTimeGMT']
                utc_datetime = datetime.fromtimestamp(date, timezone.utc)

                formatted_date = utc_datetime.strftime('%Y-%m-%d %H:%M:%S')

                start_time = convert_ts_human_to_utc(formatted_date)
                start_time = convert_utc_human_to_timezone(start_time, timezone_offset)
                #add value of respiration
                list.append((start_time, i['value'],value_user['userProfilePK']))
            #here we'll create a graph using dates and values
            dates = [item[0] for item in list]
            values = [item[1] for item in list]

            # Create graph
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=dates, y=values, mode='lines+markers', name='Fréquence cardiaque'))

            # Layout
            fig.update_layout(title='Garmin Respiration Rate Graph',
                                xaxis_title='Date',
                                yaxis_title='Respiration',
                                template='plotly_white')

            # Saves graphic as PNG image
            graph_image_path = os.path.join(report_folder, 'garmin_respiration_graph.png')
            fig.write_image(graph_image_path)

            # Open image
            with open(graph_image_path, "rb") as image_file:
                data_list = []
                graph_image_base64 = base64.b64encode(image_file.read()).decode()

                # Generate HTML to display base64-encoded image
                img_html = f'<img src="data:image/png;base64,{graph_image_base64}" alt="Garmin Respiration Graph" style="width:65%;height:auto;">'

                # Add values to report data_list
                data_list.append(('Respiration Rate Graph', img_html))

    # Report generation
    report = ArtifactHtmlReport('Garmin Respiration')
    description = 'Respiration rate on last day (measured every two minutes)'
    report.start_artifact_report(report_folder, 'Garmin_Respiration', description)
    report.add_script()
    data_headers_1 = ('Date', 'Respiration Rate', 'userid')
    report.write_artifact_data_table(data_headers_1, list, file_found)
    data_headers_2 = ('Description', 'Graph')
    report.write_artifact_data_table(data_headers_2, data_list, file_found, html_escape=False)
    report.end_artifact_report()

    # Generates TSV file
    tsvname = 'Garmin_Respiration'
    tsv(report_folder, data_headers_1, list, tsvname)

    # insert time-stamped records in timeline
    # (the first column of the table will be used to time-stamp the event)
    tlactivity = 'Garmin_Respiration'
    timeline(report_folder, tlactivity, list, data_headers_1)

