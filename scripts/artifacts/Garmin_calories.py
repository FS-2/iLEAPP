# Module Description: Parses Garmin Connect details
# Author: Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber
# Date: 05.12.2023



__artifacts_v2__ = {
    "Garmin_Connect_Calories": {
        "name": "Garmin Connect Calories",
        "description": "Extract information of Garmin Connect application",
        "author": "Romain Christen, Thibaut Frabboni, Theo Hegel, Fabrice Sieber",
        "version": "1.0",
        "date": "2023-12-05",
        "requirements": "none",
        "category": "Application",
        "notes": "",
        "paths": ('*/private/var/mobile/Containers/Data/Application/*/Library/Caches/com.pinterest.PINDiskCache.PINCacheShared/MyDayRealTimeDataService_realTimeCaloriesCacheDataKey'),
        "function": "get_garmin_calories"
    }
}
            #peut avoir plusieurs paths car tuple




import plistlib
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, convert_ts_human_to_utc, convert_utc_human_to_timezone, logdevinfo
import pytz
from datetime import datetime
from scripts.ilapfuncs import tsv
from scripts.ilapfuncs import timeline

#on définit la fonction get_garmin
#paramètres sont utilisés pour traiter des fichiers, générer des rapports,
#rechercher des informations, gérer le formatage du texte et ajuster les décalages de fuseau horaire
<<<<<<<< HEAD:scripts/artifacts/0garmin_calories.py
========

>>>>>>>> 4adbd3ef4f8fed8ed29298f03f05d9df511e1dd6:scripts/artifacts/Garmin_calories.py
def get_garmin_calories(files_found, report_folder, seeker, wrap_text, timezone_offset):
    #Cette liste sera utilisée pour stocker les données extraites
    data_list = []
    #pour chaque élément de la liste files_found, le code convertit l'élément en string
<<<<<<<< HEAD:scripts/artifacts/0garmin_calories.py
    file_found = str(files_found[0])

    # ouvre le fichier indiqué par file_found en mode binaire (indiqué par "rb") pour la lecture.
    with open(file_found, "rb") as fp:
        # charge le contenu du fichier ouvert (plist) et stocke le contenu dans la variable pl.
        contenu = plistlib.load(fp)
        root = contenu['$top']['root']
        objects = contenu['$objects']
        value_key = objects[root]['valueKey']
        real_time_calorie_data = objects[value_key]
        # Accès aux données spécifiques à RealTimeCalorieData
        active_calories_key = real_time_calorie_data['activeCaloriesKey']
        total_calories_key = real_time_calorie_data['totalCaloriesKey']

        # Obtention des valeurs associées aux clés des calories
        active_calories = objects[active_calories_key]
        total_calories = objects[total_calories_key]

        data_list.append(('Active Calories', active_calories))
        data_list.append(('Total Calories', total_calories))
        logdevinfo(f"Active Calories: {active_calories}")
        logdevinfo(f"Total Calories: {total_calories}")
========

    for file_found in files_found:
        file_found = str(file_found)
        #ouvre le fichier indiqué par file_found en mode binaire (indiqué par "rb") pour la lecture.
        #Le fichier est référencé par la variable fp dans le bloc suivant

        with open(file_found, "rb") as fp:
            #charge le contenu du fichier ouvert (plist) et stocke le contenu dans la variable pl.
            contenu = plistlib.load(fp)
            # si la clé recherchée est trouvée dans le plist (mettre la clé plist pertinente)

            root = contenu['$top']['root']
            objects = contenu['$objects']
            date_key = objects[root]['dateKey']
            value_key = objects[root]['valueKey']

            # Obtention des valeurs associées aux clés
            date_value = objects[date_key]['NS.time']
            real_time_calorie_data = objects[value_key]

            # Ajouter l'offset pour le 1er janvier 2001
            epoch_offset = datetime(2001, 1, 1).timestamp()
            adjusted_timestamp = date_value + epoch_offset

            # Convertir le timestamp en objet datetime
            date_object_utc = datetime.utcfromtimestamp(adjusted_timestamp)

            # Appliquer le fuseau horaire (par exemple, UTC+1)
            fuseau_horaire = pytz.timezone('Europe/Paris')  # Remplacez 'Europe/Paris' par votre fuseau horaire
            fuseau_horaire = pytz.timezone('Europe/Paris')
            date_object = date_object_utc.replace(tzinfo=pytz.utc).astimezone(fuseau_horaire)

            # Formater la date au format demandé
            date_formattee = date_object.strftime('%d.%m.%Y %H:%M:%S')
>>>>>>>> 4adbd3ef4f8fed8ed29298f03f05d9df511e1dd6:scripts/artifacts/Garmin_calories.py



            # Accès aux données spécifiques à RealTimeCalorieData
            active_calories_key = real_time_calorie_data['activeCaloriesKey']
            total_calories_key = real_time_calorie_data['totalCaloriesKey']


            # Obtention des valeurs associées aux clés des calories
            active_calories = objects[active_calories_key]
            total_calories = objects[total_calories_key]
    #génère le rapport HTML
<<<<<<<< HEAD:scripts/artifacts/0garmin_calories.py
    report = ArtifactHtmlReport('Garmin_Calories')
    #le report folder est définit dans l'interface graphique de iLEAPP
    report.start_artifact_report(report_folder, 'Garmin_Calories')
========

            data_list.append(('Date', date_formattee))
            data_list.append(('Active Calories', active_calories))
            data_list.append(('Total Calories', total_calories))

    report = ArtifactHtmlReport('Garmin_dernières calories')
    #le report folder est définit dans l'interface graphique de iLEAPP
    report.start_artifact_report(report_folder, 'Garmin_dernières calories')
>>>>>>>> 4adbd3ef4f8fed8ed29298f03f05d9df511e1dd6:scripts/artifacts/Garmin_calories.py
    report.add_script()
    data_headers = ('Key', 'Values')
    report.write_artifact_data_table(data_headers, data_list, file_found)


    #génère le fichier TSV
<<<<<<<< HEAD:scripts/artifacts/0garmin_calories.py
    tsvname = 'Garmin_Calories'
========
    tsvname = 'Garmin_dernières calories'
>>>>>>>> 4adbd3ef4f8fed8ed29298f03f05d9df511e1dd6:scripts/artifacts/Garmin_calories.py
    tsv(report_folder, data_headers, data_list, tsvname)

    #insérer les enregistrements horodatés dans la timeline
    #(c’est la première colonne du tableau qui sera utilisée pour horodater l’événement)
<<<<<<<< HEAD:scripts/artifacts/0garmin_calories.py
    tlactivity = 'Garmin_Calories'
========
    tlactivity = 'Garmin_dernières calories'
>>>>>>>> 4adbd3ef4f8fed8ed29298f03f05d9df511e1dd6:scripts/artifacts/Garmin_calories.py
    timeline(report_folder, tlactivity, data_list, data_headers)

    report.end_artifact_report()




