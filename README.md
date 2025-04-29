# Exth.nl Examenuitslag Checker

Dit Python-script logt automatisch in op mijn.exth.nl, downloadt het diplomavoortgangsoverzicht als PDF en controleert op afwijkingen in de inhoud.

## Functies

- Automatische inlog op mijn.exth.nl
- Downloaden van diplomavoortgang pdf bestand
- Controle op veranderingen in het pdf bestand
- Automatische e-mailmeldingen bij afwijkingen of fouten
- Uitgebreide lokale logging in `exth.log`

## Werking

1. Inloggen
   - Het script opent de inlogpagina van mijn.exth.nl.
   - Een dynamische `sSalt` wordt uit de pagina gehaald en gecombineerd met het ingestelde wachtwoord.
   - De combinatie wordt gehashed en verstuurd om veilig in te loggen.

2. Downloaden
   - Na het inloggen wordt het diplomavoortgangsoverzicht als pdf gedownload naar de lokale map van het script.

3. Bestandscontrole:
   - De inhoud van het pdf bestand wordt gecontroleerd en hier wordt een hash van gemaakt

4. Melding:
   - Bij een verandering van de inhoud stuurt het script een mail, met daarbij het pdf bestand.
   - Bij fouten verzendt het script automatisch een e-mailmelding naar het ingestelde e-mailadres.
   - Alle activiteiten worden gelogd in `exth.log` voor latere controle.
