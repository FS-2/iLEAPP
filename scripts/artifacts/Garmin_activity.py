# Module Description: Parses Garmin Connect details
# Author: Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber
# Date: 05.12.2023

__artifacts_v2__ = {
    "Garmin_Connect_4": {
        "name": "Garmin_activité",
        "description": "Extract information of Garmin Connect application",
        "author": "Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber",
        "version": "1.0",
        "date": "2023-11-30",
        "requirements": "none",
        "category": "Application",
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

from geopy.geocoders import Nominatim




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

def get_loc(latitude,longitude):
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.reverse((latitude, longitude), language='en')
    if location:
        return location.raw.get('address', {}).get('city', 'City not found')
    else:
        return 'Location pas trouvée'

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
                for cle in ['ownerId','activityName', 'calories', 'distance', 'duration', 'startTimeLocal', 'maxHR',
                            'maxSpeed', 'startLongitude', 'startLatitude']:
                    if cle in activite['NS.keys']:
                        index = activite['NS.keys'].index(cle)
                        dict_activite[cle] = activite['NS.objects'][index]  # Ajoutez la valeur au dictionnaire
                        if cle == 'distance':
                            dict_activite[cle] = activite['NS.objects'][index]/1000
                        if cle == 'duration':
                            dict_activite[cle] = activite['NS.objects'][index]/60

                    else:
                        dict_activite[cle] = 'Inconnu'

                dict_activite["Localisation"] = get_loc(dict_activite['startLatitude'], dict_activite['startLongitude'])
                liste_tuples.append(dict_activite)
                print(liste_tuples)


    reports = ArtifactHtmlReport('Garmin_Activité')
    # le report folder est définit dans l'interface graphique de iLEAPP
    reports.start_artifact_report(report_folder, 'Garmin_Activite')
    reports.add_script()
    data_headers = ("UserID", "Activité", "Calories", "Distance [km]", "Durée [min]", "Début", "maxHR", "maxSpeed [km/h]", "StartLongitude", "StartLatitude", "Localisation")

    reports.write_artifact_data_table(data_headers, [list(i.values()) for i in liste_tuples], file_found, write_total=False)

    # génère le fichier TSV
    tsvname = 'Garmin_Activité'
    tsv(report_folder, data_headers, liste_tuples, tsvname)

    # insérer les enregistrements horodatés dans la timeline
    # (c’est la première colonne du tableau qui sera utilisée pour horodater l’événement)
    tlactivity = 'Garmin_Activité'
    #timeline(report_folder, tlactivity, liste_tuples, data_headers)

    reports.end_artifact_report()