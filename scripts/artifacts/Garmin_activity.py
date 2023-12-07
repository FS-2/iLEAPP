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
        "function": "get_garmin_activite"



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


def get_garmin_activite(files_found, report_folder, seeker, wrap_text, timezone_offset):

    # pour chaque élément de la liste files_found, le code convertit l'élément en string
    liste_tuples = []
    for file_found in files_found:
        file_found = str(file_found)
        # ouvre le fichier indiqué par file_found en mode binaire (indiqué par "rb") pour la lecture.
        # Le fichier est référencé par la variable fp dans le bloc suivant

        with open(file_found, "rb") as fp:
            plist_data = plistlib.load(fp)

            contenu = resolve_uids(plist_data, plist_data['$objects'])

            root = contenu['$top']['root']  # Accéder à la racine

            # Accéder à 'valueKey' dans le dictionnaire 'root'
            value_key = root['valueKey']

            # Maintenant, accédez à 'biometricProfile' sous 'valueKey'

            for activite in value_key['NS.objects']:
                dict_activite = {}
                liste_loc = []
                for cle in ['ownerId','activityName', 'calories', 'distance', 'duration', 'startTimeLocal', 'maxHR',
                            'maxSpeed', 'startLongitude', 'startLatitude']:
                    if cle in activite['NS.keys']:
                        index = activite['NS.keys'].index(cle)
                        dict_activite[cle] = activite['NS.objects'][index]  # Ajoutez la valeur au dictionnaire
                        if cle == 'distance':
                            dict_activite[cle] = activite['NS.objects'][index]/1000
                        if cle == 'duration':
                            dict_activite[cle] = activite['NS.objects'][index]/60
                        if cle =='startLongitude':
                            liste_loc.append(activite['NS.objects'][index])
                        if cle =='startLatitude':
                            liste_loc.append(activite['NS.objects'][index])


                        if cle == 'startTimeLocal':
                            activite_date_str = activite['NS.objects'][index]

                            if activite_date_str.endswith('.0'):
                                activite_date_str = activite_date_str[:-1] + '+01:00'

                            # Gérer les secondes avec une décimal
                            if '.' in activite_date_str:
                                parts = activite_date_str.split('.')
                                activite_date_str = parts[0] + '.' + parts[1][:6]

                            activite_date = datetime.fromisoformat(activite_date_str)
                            date_timestamp = activite_date.timestamp()
                            date_object_utc = datetime.utcfromtimestamp(date_timestamp)

                            date_formatee = date_object_utc.strftime('%Y-%m-%d %H:%M:%S')

                            start_time = convert_ts_human_to_utc(date_formatee)
                            start_time = convert_utc_human_to_timezone(start_time, timezone_offset)
                            dict_activite[cle] = start_time

                    else:
                        dict_activite[cle] = 'Inconnu'
                if len(liste_loc) != 0:
                    try:
                        geolocator = Nominatim(user_agent="geoapiExercises")
                        location = geolocator.reverse((liste_loc[1], liste_loc[0]))
                        dict_activite["Adresse"] = location
                    except (GeocoderTimedOut, GeocoderServiceError) as e:
                        # Handle specific geolocation errors here.
                        dict_activite["Adresse"] = "Inconnu"

                    else:
                        dict_activite["Adresse"] = "Inconnu"
                else:
                    dict_activite["Adresse"] = "Inconnu"


                liste_tuples.append(dict_activite)



    reports = ArtifactHtmlReport('Garmin_Activity')
    # le report folder est définit dans l'interface graphique de iLEAPP
    reports.start_artifact_report(report_folder, 'Garmin_Activity')
    reports.add_script()
    data_headers = ("UserID", "Activity", "Calories", "Distance [km]", "Duration [min]", "Start Date", "maxHR", "maxSpeed [km/h]", "StartLongitude", "StartLatitude", "adress")

    reports.write_artifact_data_table(data_headers, [list(i.values()) for i in liste_tuples], file_found, write_total=False)

    # génère le fichier TSV
    tsvname = 'Garmin_Activity'
    tsv(report_folder, data_headers, liste_tuples, tsvname)

    # insérer les enregistrements horodatés dans la timeline
    # (c’est la première colonne du tableau qui sera utilisée pour horodater l’événement)
    tlactivity = 'Garmin_Activity'
    #timeline(report_folder, tlactivity, liste_tuples, data_headers)

    reports.end_artifact_report()