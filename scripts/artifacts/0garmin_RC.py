# Module Description: Parses Garmin Connect details
# Author: Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber
# Date: 05.12.2023

__artifacts_v2__ = {
    "Garmin_Connect": {               #jsp si faut plusieurs scripts avec chaque fois 1 trace ou 1 seul pour tout
        "name": "Garmin Connect",
        "description": "Extract information of Garmin Connect application",
        "author": "Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber",
        "version": "1.0",
        "date": "2023-12-05",
        "requirements": "none",
        "category": "Application",
        "notes": "",
        "paths": ('*/root/private/var/mobile/Containers/Data/Application/*/Library/Caches/com.pinterest.PINDiskCache.PINCacheShared/MyDayRealTimeDataService_realTimeCaloriesCacheDataKey'),      #peut avoir plusieurs paths car tuple
        "function": "get_garmin"                                  #pas oublier étoile à la fin du path pour.wall et .db
    }
}



import plistlib

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, convert_ts_human_to_utc, convert_utc_human_to_timezone, logdevinfo

#permet de parcourir la liste des fichiers qui ont été trouvés à partir de paths et,
#dans le cas des bases de données SQLite, de bien sélectionner le fichier de la base de données
#et non les fichiers -journal et -wal.
def get_garmin(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('/Accounts3.sqlite'):
            break

def get_appleWifiPlist(files_found, report_folder, seeker, wrap_text, timezone_offset):
    known_data_list = []
    scanned_data_list = []
    known_files = []
    scanned_files = []
    for file_found in files_found:
        file_found = str(file_found)

        with open(file_found, 'rb') as f:
            deserialized = plistlib.load(f)
            if 'CachedData<RealTimeCalorieData>' in deserialized:
                val = (deserialized['dateKey'])
                logdevinfo(f"Keep Wifi Powered Airplane Mode: {val}")

            #if 'List of known networks' in deserialized:
                #known_files.append(file_found)
                #for known_network in deserialized['List of known networks']:
                    #ssid = ''
    
