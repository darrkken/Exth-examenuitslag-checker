# Exth.nl Examenuitslag Checker

Dit Python-script logt automatisch in op mijn.exth.nl, downloadt het diplomavoortgangsoverzicht als PDF en controleert op afwijkingen in bestandsgrootte.

## Functies

- Automatische inlog op mijn.exth.nl
- Download van diplomavoortgang PDF-bestand
- Groottecontrole binnen ingestelde marge
- Automatische e-mailmeldingen bij afwijkingen of fouten
- Uitgebreide lokale logging in `exth.log`

## Werking

1. Inloggen
   - Het script opent de inlogpagina van mijn.exth.nl.
   - Een dynamische `sSalt` wordt uit de pagina gehaald en gecombineerd met het ingestelde wachtwoord.
   - De combinatie wordt gehashed en verstuurd om veilig in te loggen.

2. Downloaden
   - Na het inloggen wordt het diplomavoortgangsoverzicht als PDF gedownload naar de lokale map van het script.

3. Bestandscontrole:
   - De grootte van het gedownloade PDF-bestand wordt gecontroleerd.
   - In het script stel je een referentie_grootte en een toegestande_afwijking in. 

4. Melding:
   - Bij afwijkingen of fouten verzendt het script automatisch een e-mailmelding naar het ingestelde e-mailadres.
   - Alle activiteiten worden gelogd in `exth.log` voor latere controle.
