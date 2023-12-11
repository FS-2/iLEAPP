# Module Description: Get information related to heart rate on last day
# Requirements: pip install plotly (To create a graph)
#               pip install kaleido (To export a static image from plotly)
# Author: Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber
# Date: 08.12.2023

__artifacts_v2__ = {
    "Garmin_Connect_Heart": {
        "name": "Garmin Heart",
        "description": "Extract information of Garmin Connect application",
        "author": "Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber",
        "version": "1.0",
        "date": "2023-12-05",
        "requirements": "none",
        "category": "Garmin Application",
        "notes": "",
        "paths": ('*/private/var/mobile/Containers/Data/Application/*/Library/Caches/com.pinterest.PINDiskCache.PINCacheShared/MyDaySeverDataHelper%2EallDayTimeline'),
        "function": "get_garmin_heart"
    }
}

import plistlib
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import tsv, timeline, convert_ts_human_to_utc, convert_utc_human_to_timezone
from datetime import datetime, timezone
import plotly.graph_objects as go
import base64
import os

# Function to simplify data storage (resolve UIDs)
def resolve_uids(item, objects):
    if isinstance(item, plistlib.UID):
        return resolve_uids(objects[item.data], objects)
    elif isinstance(item, dict):
        return {key: resolve_uids(value, objects) for key, value in item.items()}
    elif isinstance(item, list):
        return [resolve_uids(value, objects) for value in item]
    else:
        return item

def get_garmin_heart(files_found, report_folder, seeker, wrap_text, timezone_offset):
    # Create an empty list to store extracted data
    data_list = []
    # Convert elements to string
    for file_found in files_found:
        file_found = str(file_found)

        # Opening and loading the file
        with open(file_found, "rb") as file:
            list = []
            plist_data = plistlib.load(file)

            content = resolve_uids(plist_data, plist_data['$objects']) # Simplify data storage format
            root = content['$top']['root']  # Go to root

            value_key = root['allDayHeartRateKey']['heartRateValues']['NS.objects']
            value_user = root['allDayHeartRateKey']

            # Accesses 'valueKey' in the 'root' dictionary
            for i in value_key:
                date = i['NS.objects'][0]/1000
                utc_datetime = datetime.fromtimestamp(date, timezone.utc)
                formatted_date = utc_datetime.strftime('%Y-%m-%d %H:%M:%S')
                start_time = convert_ts_human_to_utc(formatted_date)
                start_time = convert_utc_human_to_timezone(start_time, timezone_offset)
                list.append((start_time, i['NS.objects'][1], value_user['userProfilePK']))

            # Creates graph with dates and values
            dates = [item[0] for item in list]
            values = [item[1] for item in list]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=dates, y=values, mode='lines+markers', name='Fréquence cardiaque'))

            # Layout
            fig.update_layout(title='Garmin Heart Rate Graph',
                                xaxis_title='Date',
                                yaxis_title='Heart rate',
                                template='plotly_white')

            # Saves graphic as PNG image
            graph_image_path = os.path.join(report_folder, 'garmin_heart_graph.png')
            fig.write_image(graph_image_path)

            # Open image
            with open(graph_image_path, "rb") as image_file:
                graph_image_base64 = base64.b64encode(image_file.read()).decode()

                # Generate HTML to display base64-encoded image
                img_html = f'<img src="data:image/png;base64,{graph_image_base64}" alt="Garmin Heart Graph" style="width:65%;height:auto;">'

                # Add values to report data_list
                data_list.append(('Heart Rate Graph', img_html))

    # Generates report
    report = ArtifactHtmlReport('Garmin Heart')
    description = 'Heart rate on last day (measured every two minutes)'
    report.start_artifact_report(report_folder, 'Garmin_Heart', description)
    report.add_script()
    data_headers_1 = ('Date', 'Heart Rate', 'userId')
    report.write_artifact_data_table(data_headers_1, list, file_found)
    data_headers_2 = ('Description', 'Graph')
    report.write_artifact_data_table(data_headers_2, data_list, file_found, html_escape=False)
    report.end_artifact_report()

    # Generates TSV file
    # The second table (with headers_2) is not generated as a TSV file because it contains a base64 image (unreadable)
    tsvname = 'Garmin_Heart'
    tsv(report_folder, data_headers_1, list, tsvname)

    # Insert time-stamped records in timeline
    # (the first column of the table will be used to time-stamp the event)
    tlactivity = 'Garmin_Heart'
    timeline(report_folder, tlactivity, list, data_headers_1)

