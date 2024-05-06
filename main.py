# STRUCTURE: <body> <div class ="aw-weekly-menu aw-group-5" = 0$> <tbody class="today">

import requests as req
from bs4 import BeautifulSoup
import csv
# Mail
import smtplib

# Für das Auslesen des Google-Dokuments
from google.oauth2 import service_account
from googleapiclient.discovery import build

from dotenv import load_dotenv
import os

import json


def fetch_menu(link_to_menu):
    soup = BeautifulSoup(link_to_menu.content, 'html.parser')
    menu_raw = []
    menu_raw = (soup.find_all("tr"))

    dates = str(soup.find('tr', class_='today'))
    dates = dates.split('</p>')

    for t in range(len(dates)):
        dates[t] = dates[t][-10:]
    del dates[-1]
    print("Dates retrieved")

    for i in [0, 0, 1, 2, 3]:
        menu_raw.pop(i)
    for i in range(len(menu_raw)):
        menu_raw[i] = str(menu_raw[i]).split('</td>')
    print("Menu fetched")

    menu = [[] for _ in range(5)]

    for i in menu_raw:
        for j in range(len(i) - 1):
            i[j] = i[j].replace('\xa0', '')
            menu[j].append(i[j])

    for j in range(len(menu)):
        for i in range(len(menu[j])):
            txt = """%s""" % menu[j][i]
            soup = BeautifulSoup(txt, 'html.parser')

            menu[j][i] = str(soup.get_text()).split('/')

            for f in range(1, len(menu[j][i])):
                menu[j][i][f] = menu[j][i][f][6:-3]
            menu[j][i][0] = menu[j][i][0][:-3]
            del menu[j][i][-1]
    # print(menu_raw)
    return menu, dates


def format_menu(menu):
    days = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]
    dishes = ["Suppe", "Hauptgericht", "Beilage", "Nachspeise"]
    text = ""
    # print("Menu: ")

    for i in range(len(menu)):
        text += days[i] + ':' + '\n\n'
        for j in range(len(menu[i])):
            text += dishes[j] + ':' + '\n'
            for k in range(len(menu[i][j])):
                text += menu[i][j][k][:-3] + '\t' + menu[i][j][k][-3:] + '\n'
            text += '\n\n'

    return text


def save_menu(menu, dates, alltime_menu):
    for i in range(len(menu)):
        for j in range(len(menu[i])):
            for k in range(len(menu[i][j])):

                if menu[i][j][k] in alltime_menu[0]:
                    index = alltime_menu[0].index(menu[i][j][k])
                    alltime_menu[1][index] += ", " + dates[i]

                else:
                    alltime_menu[0].append(menu[i][j][k])
                    alltime_menu[1].append(dates[i])

    print("All-time menu updated")
    return alltime_menu


def find_favs(favorites, menu, dates):
    matches = [[], [], []]

    for index, matches_int in enumerate(favorites):
        for g in range(len(menu)):
            for h in range(len(menu[g])):
                for w in range(len(menu[g][h])):
                    if matches_int in menu[g][h][w]:
                        matches[0].append(menu[g][h][w])
                        matches[1].append(dates[g])
                        matches[2].append(index)

    print("Favorites searched")
    return matches


def prepare_data(full_menu):
    csv_menu = []
    for i in range(len(full_menu[0])):
        csv_menu.append([full_menu[0][i][:-3], full_menu[0][i][-3:], full_menu[1][i]])
    # print(csv_menu)
    return csv_menu


def write_file(prepared_data):
    with open('output.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(prepared_data)


def send_mail(matches, menu, wishing_list, dates, sender, recipient, password, server, port, username=None):
    if username is None:
        username = sender

    sending_person = "MensaBot <{}>".format(sender)
    receiving_person = "Mensageher <{}>".format(recipient)
    subject = "Speiseplan"
    message = ""

    # if len(matches[0]) == 0:
    #     return

    if len(matches[0]) == 1:
        subject = str(wishing_list[matches[2][0]]) + " am " + str(matches[1][0]) + "!"
        message = "Dein von dir gewünschtes Gericht " + str(wishing_list[matches[2][0]]) + " gibt es am " \
                  + str(matches[1][0]) + " als " + str(matches[0][0][:-3]) + " für " + str(
            matches[0][0][-3:]) + " Euronen" + "\n \n"

    elif len(matches[0]) > 1:
        subject = str(len(matches[0])) + " Wunschgerichte " + str(dates[0]) + " - " + str(dates[-1])
        message = "In der Woche vom " + str(dates[0]) + " - " + str(
            dates[-1]) + " gibt es folgende deiner Lieblingsgerichte: \n \n"
        text = ""
        for i in range(len(matches[0])):
            text += str(wishing_list[matches[2][i]]) + ": " + str(matches[0][i][:-3]) + "\t" + str(
                matches[1][i]) + "\t" + str(matches[0][0][-3:]) + "\n"
        text += "\n \n"
        message += text

    menu_text = "Gesamter Speiseplan " + str(dates[0]) + " - " + str(dates[-1]) + ":\n \n"
    all_text = message + menu_text + menu
    mail_text = "Subject: {}\nTo: {}\nFrom: {}\n\n{}".format(subject, receiving_person, sending_person, all_text)

    with smtplib.SMTP(server, int(port)) as smtp:
        smtp.starttls()
        smtp.login(username, password)
        smtp.sendmail(sending_person, receiving_person, mail_text)

    print("Mail sent")


def get_wishes(service_account_file, document_id):
    # Pfad zum Service-Konto-Schlüssel (JSON-Datei)
    # service_account_file = 'service_account_credentials.json'

    # Erstellen der Zugangsdaten mit dem Service-Konto-Schlüssel
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=['https://www.googleapis.com/auth/documents.readonly'])
    # Google Docs API-Client erstellen
    service = build('docs', 'v1', credentials=credentials)

    # Die ID des Google-Dokuments angeben
    # document_id = ''

    # Text aus dem Google-Dokument abrufen
    document = service.documents().get(documentId=document_id).execute()
    doc_content = document.get('body').get('content')

    # Text aus dem Inhalt des Dokuments extrahieren
    extracted_text = ''
    for content in doc_content:
        if 'paragraph' in content:
            for element in content['paragraph']['elements']:
                text_run = element.get('textRun')
                if text_run:
                    extracted_text += text_run['content']

    print("Wishes extracted")
    return str(extracted_text)[:-1].split(",")


def create_service_account_json():
    project_id = os.getenv('PROJECT_ID')
    private_key_id = os.getenv('PRIVATE_KEY_ID')
    private_key = os.getenv('PRIVATE_KEY')
    client_email = os.getenv('CLIENT_EMAIL')
    client_id = os.getenv('CLIENT_ID')
    client_x509_cert_url = os.getenv('CLIENT_URL')

    credentials_dict = {
        "type": "service_account",
        "project_id": project_id,
        "private_key_id": private_key_id,
        "private_key": private_key,
        "client_email": client_email,
        "client_id": client_id,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": client_x509_cert_url,
        "universe_domain": "googleapis.com"
    }
    # print(credentials_dict)
    # print(credentials_dict['private_key'])

    # Pfad zur JSON-Datei
    json_file_path = "service_account_credentials.json"

    # JSON-Datei erstellen
    with open(json_file_path, "w") as outfile:
        json.dump(credentials_dict, outfile, indent=2)

    # Öffne die Datei erneut und bearbeite den Inhalt, um doppelte Backslashes zu entfernen
    with open(json_file_path, "r") as infile:
        data = infile.read()

    # Entferne doppelte Backslashes
    data = data.replace("\\\\", "\\")

    # Schreibe den bearbeiteten Inhalt zurück in die Datei
    with open(json_file_path, "w") as outfile:
        outfile.write(data)

    return json_file_path


def main():
    load_dotenv()
    sender = os.getenv('SENDER')
    password = os.getenv('PASSWORD')
    recipient = os.getenv('RECIPIENT')
    doc_id = os.getenv('DOC_ID')
    mail_server = os.getenv('MAIL_SERVER')
    mail_port = os.getenv('MAIL_PORT')
    username = os.getenv('USER')

    create_service_account_json()

    link_to_menu = req.get('https://www.mensaplan.de/regensburg/mensa-oth-regensburg/index.html')

    wish_dishes = get_wishes('service_account_credentials.json', doc_id)
    # print(wish_dishes)

    alltime_menu = [[], []]

    menu, dates = fetch_menu(link_to_menu)
    menu_text = format_menu(menu)
    # print(menu_text)

    matches = find_favs(wish_dishes, menu, dates)
    full_menu = save_menu(menu, dates, alltime_menu)

    prepared_data = prepare_data(full_menu)
    # write_file(prepared_data)

    send_mail(matches, menu_text, wish_dishes, dates, sender, recipient, password, mail_server, mail_port, username)


if __name__ == "__main__":
    main()
