__artifacts_v2__ = {
    "Garmin_Connect_Pay": {
        "name": "Garmin Pay",
        "description": "Get information related to credit card",
        "author": "Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber",
        "version": "1.0",
        "date": "2023-12-12",
        "requirements": "none",
        "category": "Garmin Application",
        "notes": "",
        "paths": ('*/private/var/mobile/Containers/Data/Application/*/Library/Caches/GarminPayImageCache/FitPayCardImage*'),
        "function": "get_garmin_pay"
    }
}

import base64
from scripts.artifact_report import ArtifactHtmlReport

def get_garmin_pay(files_found, report_folder, seeker, wrap_text, timezone_offset):
    # Create an empty list to store extracted data
    data_list = []
    # Convert elements to string
    for file_found in files_found:
        file_found = str(file_found)

        # Read the image and encode it in base64
        with open(file_found, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode()
            # Generate the HTML to display the image encoded in base64
            img_html = f'<img src="data:image/png;base64,{encoded_image}" alt="Garmin Pay Image" style="width:35%;height:auto;">'

            # Adding values to report data_list
            data_list.append(('Credit card image', img_html))

    # Generates report
    report = ArtifactHtmlReport('Garmin Pay')
    description = "Credit card information"
    report.start_artifact_report(report_folder, 'Garmin_Pay', description)
    report.add_script()
    data_headers = ('Key', 'Value')
    report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
    report.end_artifact_report()

    # No TSV file is generated because the table contains base64 images (unreadable)

    # Nothing is inserted in timeline because there are no time-stamped records