# -*- coding: utf-8 -*-
import requests
import re
import hashlib
import os
import smtplib
import time
from datetime import datetime
from email.message import EmailMessage
import pypdf 

# ---------------------- zelf in te vullen ----------------------

# E-mail instellingen. Makkelijkste manier is om en app-wachtwoord te gebruiken.
# Dit kan je instellen in je Google-account onder 'Beveiliging' > 'App-wachtwoorden'.
smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_username = "jouw-emailadres@gmail.com"
smtp_password = "jouw-app-wachtwoord"
ontvanger_email = "jouw-ontvanger@example.com" #Het email adres waarop je de mails moet ontvangen

# Mijn.exth inlog gegevens
login_username = "mijn.exth gebruikersnaam"
login_password = "mijn.exth wachtwoord"

# ---------------------- Python code, niet aanpassen ----------------------

script_dir = os.path.dirname(os.path.abspath(__file__))
logbestand = os.path.join(script_dir, "exth.log")
pdf_naam = os.path.join(script_dir, "diplomavoortgang.pdf")
referentie_hash_file = os.path.join(script_dir, "referentie_hash.txt")

def bereken_hash_van_inhoud(bestandspad):
    try:
        with open(bestandspad, "rb") as f:
            reader = pypdf.PdfReader(f)  # Gebruik pypdf.PdfReader
            inhoud = ""
            for pagina in reader.pages:
                inhoud += pagina.extract_text() or ""
            if not inhoud.strip():
                log_bericht("PDF bevat geen tekstinhoud.")
                return None
        return hashlib.sha256(inhoud.encode("utf-8")).hexdigest()
    except Exception as e:  # Gebruik een algemene Exception (pypdf heeft geen specifieke PdfReadError)
        log_bericht(f"Fout bij lezen van PDF: {e}")
        return None

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
        with requests.Session() as session:
            url = "https://mijn.exth.nl/index.php"
            response = session.get(url)
            if response.status_code != 200:
                foutmelding(f"Fout bij ophalen van loginpagina. Statuscode: {response.status_code}")
                return
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
        if post_response.status_code != 200:
            foutmelding(f"Fout bij POST-login. Statuscode: {post_response.status_code}")
            return
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
        huidige_hash = bereken_hash_van_inhoud(pdf_naam)
        if huidige_hash is None:
            foutmelding("Kon hash van inhoud niet berekenen.")
            return

        if not os.path.exists(referentie_hash_file):
            log_bericht("Geen referentiehash gevonden. Eerste keer uitvoeren.")
            with open(referentie_hash_file, "w") as f:
                f.write(huidige_hash)
            log_bericht("Referentiehash opgeslagen. Geen e-mail verzonden.")
            return

        with open(referentie_hash_file, "r") as f:
            referentie_hash = f.read().strip()

        if huidige_hash != referentie_hash:
            verzend_email(
                "Diplomavoortgang: Inhoud gewijzigd",
                f"De inhoud van het bestand is gewijzigd. Nieuwe hash: {huidige_hash}",
                bijlage_pad=pdf_naam
            )
            log_bericht(f"Inhoud wijziging gedetecteerd. Nieuwe hash: {huidige_hash}")

            with open(referentie_hash_file, "w") as f:
                f.write(huidige_hash)
        else:
            log_bericht("Geen inhoud wijziging gedetecteerd.")

        time.sleep(2)
        os.remove(pdf_naam)
        log_bericht("PDF-bestand verwijderd.")
    except Exception as e:
        foutmelding(f"Fout bij controle of verwijderen van PDF: {e}")
        return

if __name__ == "__main__":
    main()

