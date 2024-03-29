# Fritz DECT200 (11081)
Dieser Baustein liest den aktuellen Stromverbrauch in mW, den Zählerstand des DECT200 in Wh und die gemessene Temperatur (korrigiert um den eingestellten Offset). Mehrere Bausteine
können als Kaskade verknüpft werden, sodass nur eine Webabfrage nötig wird. Hierzu wird einfach A6 des Vorgängerbausteins mit E1 des Nachfolgebausteins verknüpft.

## Voraussetzung
- HS Firmware 4.11 / HSL 2.0.4

## Installation
Die .hslz Datei mit dem Gira Experte importieren. Das Logikmodul ist dann in der Rubrik "Datenaustausch" verfügbar.

## Eingänge

| Eingang       | Initwert | Beschreibung                                                                                                                                                                                                    |
|---------------|----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| XML           |          | Kaskadeneingang (XML-Ausgang eines anderen DECT200 bausteins.<br>So muss nicht jeder Baustein eine Verbindung zur FritzBox aufbauen.<br>Be den Bausteinen in der Kaskade, den Eingang 'Intervall' auf 0 setzen. |
| SID           |          | Mit der FritzBox ausgehandelte "verschlüsselte" ID. Wird nicht vom Nutzer erzeugt, sondern kann den Bausteinen von einer anderen FritzBox-Baustein zur Verfügung gestellt werden.                               | 
| Fritzbox IP   |          | IP der FritzBox                                                                                                                                                                                                 |
| User@Passwort |          | `User@Passwort` des zu verwendenden FritzBox-Nutzers, also Nutzername @ Passwort                                                                                                                                |
| AIN           |          | AIN der auszulesenden FritzDECT200 im Format '12345 6789123'                                                                                                                                                    |
| Ein/Aus       | 0        | Ein/Ausschalten der FritzDECT 200                                                                                                                                                                               |
| Timeout SID   | 480      | Dauer, nach der eine neue SID ausgehandelt werden soll, um einen Timeout seitens der FritzBox zuvor zu kommen.                                                                                                  |
| Intervall [s] | 0        | Bei einem Wert > 0 wird der Status des DECT200-Geräts alle x Sekunden von der Fritzbox abgefragt.                                                                                                               |



## Ausgänge
Alle Ausgänge sind SBC / Send by Change ausgeführt.

| Ausgang               | Initwert | Beschreibung                                                     |
|-----------------------|----------|------------------------------------------------------------------|
 | Name                  |          | Name der Steckdose in der FritzBox-Oberfläche                    |
 | RM Present            | 0        | 0 = Steckdose ist nicht erreichbar, 1 = Steckdose ist erreichbar |
| RM Ein/Aus            | 0        | Ein/Aus Status der DECT200                                       |
| RM Akt. mW            | 0        | Gelesene mW                                                      |
| RM Akt. Zaehlerst. Wh | 0        | Gelesene Wh                                                      |
| RM Akt. Temp. °C      | 0        | Gelesene °C, um Offset korrigiert                                |
| SID                   |          | Aktuelle SID (Nur beim 1. Baustein einer Kaskade!)               |
| XML                   |          | Empfangene XML Datei zu allen Smart Home Geräten der FritzBox    |


## Sonstiges

- Neuberechnung beim Start: Nein
- Baustein ist remanent: Nein
- Interne Bezeichnung: 11081

### Change Log

- V2.2:
  - Bug: Fixed no ain during init
- V2.1
  - Bug: Fixed output of name
  - Bug: Fixed output of temperature
  - Bug: Fixed missing output after set switch
- v2.0
  - Impr.: Ausgabe von Name [#8](https://github.com/En3rGy/11081-Fritz-DECT200/issues/8)
  - Impr.: Ausgabe Present-Status [#7](https://github.com/En3rGy/11081-Fritz-DECT200/issues/7)
  - Impr.: Anpassung Debug-Umgebung
- v1.7
  - Impr.: [#4](https://github.com/En3rGy/11081-Fritz-DECT200/issues/4) Try-catch für einzelne Datenpunkte, damit im Fehlerfall die anderen noch verarbeitet werden können
- v1.6
  - Impr.: [#3](https://github.com/En3rGy/11081-Fritz-DECT200/issues/3) Logging mit AIN-Angabe
- v1.4 & v1.5
  - Fix: [#1](https://github.com/En3rGy/11081-Fritz-DECT200/issues/1) Keine Reaktion auf Intervall-Vorgabe
- v1.3
  - Impr.: Exception Handling
  - Impr.: Impr. logging (msg bei xml abruf)
- v1.2
  - Fix: Intervall triggert nicht
- v1.1
  - Fix: SBC
- v1.0
  - Impr.: Trigger Eingang in Intervall-Eingang geändert (autom. Abruf)
  - Impr.: Ausgänge als SBC ausgeführt
- v0.19
  - Impr.: Ausgaben auf Debug-Seite
- v0.18
  - Bugfix: XML Daten wurden nicht auf Ausgang "XML" weitergereicht.

### Open Issues / Known Bugs

- Eingang Timeout SID aktuell ohne Funktion

### Support

Für Fehlermeldungen oder Feature-Wünsche, bitte [github issues](https://github.com/En3rGy/11081-Fritz-DECT200/issues) nutzen.
Fragen am besten als Thread im [knx-user-forum.de](https://knx-user-forum.de) stellen. Dort finden sich ggf. bereits Diskussionen und Lösungen.

## Code

Der Code des Bausteins befindet sich in der hslz Datei oder auf [github](https://github.com/En3rGy/11081-Fritz-DECT200).

### Entwicklungsumgebung

- [Python 2.7.18](https://www.python.org/download/releases/2.7/)
    - Install python *markdown* module (for generating the documentation) `python -m pip install markdown`
- Python editor [PyCharm](https://www.jetbrains.com/pycharm/)
- [Gira Homeserver Interface Information](http://www.hs-help.net/hshelp/gira/other_documentation/Schnittstelleninformationen.zip)

## Anforderungen

-

## Software Design Description

-

## Validierung und Verifikation

-

## Lizenz

Copyright 2021 T. Paul

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
