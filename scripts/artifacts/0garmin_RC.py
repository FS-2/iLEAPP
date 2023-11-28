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
        "paths": ('*/mobile/Library/Accounts/Accounts3.sqlite*'),      #peut avoir plusieurs paths car tuple
        "function": "get_garmin"                                  #pas oublier étoile à la fin du path pour.wall et .db
    }
}

#TOUT EST A TITRE D'EXEMPLE CAR NOUS ON AURA DU JSON SURTOUT

import sqlite3
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone

#permet de parcourir la liste des fichiers qui ont été trouvés à partir de paths et,
#dans le cas des bases de données SQLite, de bien sélectionner le fichier de la base de données
#et non les fichiers -journal et -wal.
def get_garmin(files_found, report_folder, seeker, wrap_text, timezone_offset):
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('/Accounts3.sqlite'):
            break

#base de données est ouverte en lecture seule
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()

#La requête, écrite et testée dans le logiciel de visualisation des bases de données SQLite,
# est ensuite insérée en l’état dans cursor.execute
cursor.execute('''
    select blalba requête sql
'''
    )
