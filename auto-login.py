# -*- coding: utf-8 -*-
import requests
import re
import hashlib
import os
import smtplib
import time
from datetime import datetime
from email.message import EmailMessage

# Bepaal veilig de map waar dit script staat
script_dir = os.path.dirname(os.path.abspath(__file__))

# Bestandslocaties
logbestand = os.path.join(script_dir, "exth.log")
pdf_naam = os.path.join(script_dir, "diplomavoortgang.pdf")

# Instellingen
referentie_grootte = 744
toegestane_afwijking = 7  # bytes

# E-mail instellingen
smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_username = "jouw-emailadres@gmail.com"
smtp_password = "jouw-app-wachtwoord"
ontvanger_email = "jouw-ontvanger@example.com"

# Login-instellingen
login_username = "test@test.nl"
login_password = "mijnwachtwoord"

def log_bericht(tekst):
    tijd = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(logbestand, "a") as log:
        log.write(f"[{tijd}] {tekst}\n")

def verzend_email(onderwerp, melding, bijlage_pad=None):
    try:
        msg = EmailMessage()
        msg["Subject"] = onderwerp
        msg["From"] = smtp_username
        msg["To"] = ontvanger_email
        msg.set_content(melding)

        if bijlage_pad and os.path.exists(bijlage_pad):
            with open(bijlage_pad, "rb") as f:
                pdf_data = f.read()
            msg.add_attachment(pdf_data, maintype="application", subtype="pdf", filename=os.path.basename(bijlage_pad))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)

        log_bericht(f"E-mail verzonden: {onderwerp}")
    except Exception as e:
        log_bericht(f"Fout bij verzenden van e-mail: {e}")

def foutmelding(melding):
    log_bericht(f"Fout: {melding}")
    verzend_email("Diplomavoortgang: Foutmelding", melding)

def main():
    log_bericht("Script gestart.")
    try:
        session = requests.Session()
        url = "https://mijn.exth.nl/index.php"
        response = session.get(url)
        html = response.text
    except Exception as e:
        foutmelding(f"Fout bij ophalen van loginpagina: {e}")
        return

    try:
        salt_match = re.search(r"var sSalt = '(\d+)';", html)
        if not salt_match:
            foutmelding("Geen sSalt gevonden op loginpagina.")
            return
        sSalt = salt_match.group(1)
    except Exception as e:
        foutmelding(f"Fout bij zoeken naar sSalt: {e}")
        return

    def md5(s): return hashlib.md5(s.encode("utf-8")).hexdigest()
    try:
        hashed_password = md5(sSalt + md5(login_password))
    except Exception as e:
        foutmelding(f"Fout bij genereren van hash: {e}")
        return

    payload = {
        "redirect": "/index.php?action=download_diplomavoortgang",
        "username": login_username,
        "password": hashed_password,
        "tck22605": login_password,
        "keep_login": "",
    }

    try:
        post_response = session.post(url, data=payload, allow_redirects=True)
    except Exception as e:
        foutmelding(f"Fout bij POST-login: {e}")
        return

    if "application/pdf" not in post_response.headers.get("Content-Type", ""):
        foutmelding(f"Geen PDF gedownload. Content-Type: {post_response.headers.get('Content-Type', 'onbekend')}")
        return

    try:
        with open(pdf_naam, "wb") as f:
            f.write(post_response.content)
    except Exception as e:
        foutmelding(f"Fout bij opslaan van PDF: {e}")
        return

    try:
        bestandsgrootte = os.path.getsize(pdf_naam)
        verschil = abs(bestandsgrootte - referentie_grootte)

        if verschil > toegestane_afwijking:
            verzend_email(
                "Diplomavoortgang: Grootte afwijking gedetecteerd",
                f"Afwijking: {bestandsgrootte} bytes (verschil: {verschil} bytes)",
                bijlage_pad=pdf_naam
            )
            log_bericht(f"Grootte afwijking gemeld: {bestandsgrootte} bytes")
        else:
            log_bericht(f"Bestandsgrootte binnen marge: {bestandsgrootte} bytes")

        time.sleep(2)
        os.remove(pdf_naam)
        log_bericht("PDF-bestand verwijderd.")
    except Exception as e:
        foutmelding(f"Fout bij controle of verwijderen van PDF: {e}")
        return

if __name__ == "__main__":
    main()

