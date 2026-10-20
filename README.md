# sailcrawl

Crawler für Satellitenbilder und Eiskarten von Grönland ([DMI](http://ocean.dmi.dk/arctic/)).
Neue Bilder werden heruntergeladen, per Mail an Abonnenten verschickt und optional in eine Nextcloud hochgeladen.

## Installation

```bash
pip3 install --user -r requirements.txt
```

## Konfiguration

`config.template.json` kopieren und anpassen:

```bash
cp config.template.json config.json
```

| Schlüssel | Beschreibung |
|---|---|
| `smtp` | Zugangsdaten des Mailservers (SSL) |
| `subscribers` | Empfänger mit Liste der gewünschten Orte (`sattelite_images`) und Eiskarten (`icecharts`). Gültige Namen stehen im `urls`-Dictionary in `crawl.py`. |
| `upload_to_nextcloud` | `true`, um neue Bilder in die Nextcloud hochzuladen |
| `nextcloud.url` | WebDAV-Ordner, z.B. `https://cloud.example.com/remote.php/dav/files/<user>/<ordner>` |
| `known_urls_file` | Optional. Datei mit bereits verarbeiteten URLs. Standard: `known_urls_<configname>.txt` |

Konfigurationsdateien mit Zugangsdaten (`config.json`, `config-archive.json`) sind in `.gitignore` eingetragen.

## Ausführen

```bash
python3 crawl.py config.json
```

Das Script ist für regelmässige Ausführung gedacht (z.B. Aufgabenplaner der Synology NAS oder cron).
Pro Lauf werden nur Bilder verarbeitet, deren URL noch nicht in der Known-URLs-Datei steht.
Heruntergeladene Dateien landen im Ordner `images/`.

## Fehlerbehandlung

- **Nextcloud `423 Locked`**: Die Zieldatei ist auf dem Server gesperrt. Das passiert z.B. nach einem abgebrochenen Upload oder wenn die Datei in einem Client geöffnet ist. Das Script versucht den Upload bis zu 3× im Abstand von 30 s. Schlägt er weiterhin fehl, wird der Fehler geloggt und der Lauf fortgesetzt.
- Bleibt eine Sperre bestehen, läuft sie nach der Lock-TTL ab (Standard 1 h). Sofort lösen lässt sie sich nur serverseitig: Mit Redis als Locking-Backend den Redis-Cache leeren, sonst die Einträge in der Tabelle `oc_file_locks` löschen (Nextcloud vorher in den Maintenance-Mode setzen).
