# Fronius Fake Meter

Dieses Projekt erstellt einen Modbus-Slave für die Integration mit einer Fronius Wallbox und anderen Systemen, die Modbus TCP unterstützen.

## Einrichtung

### Voraussetzungen

- Raspberry Pi mit Raspberry Pi OS
- Python 3.x
- Pymodbus und Requests Bibliotheken

### Installation

1. Klone das Repository auf den Raspberry Pi:

    ```bash
    git clone https://github.com/dein-benutzername/fronius-fake-meter.git
    cd fronius-fake-meter
    ```

2. Installiere die Abhängigkeiten:

    ```bash
    pip3 install -r requirements.txt
    ```

3. Passe die Konfigurationsdateien in `config/` für jeden Kollegen an (LIND.json, STANGL.json, etc.).

4. Teste das Skript:

    ```bash
    python3 fronius_fake_meter.py
    ```

5. Stelle sicher, dass das automatische Update funktioniert, indem du das `update.sh` Skript über einen Cronjob alle 59 Minuten ausführst.

### Cronjob für Auto-Update

Um das Auto-Update alle 59 Minuten zu aktivieren, füge folgenden Cronjob hinzu:

```bash
crontab -e
