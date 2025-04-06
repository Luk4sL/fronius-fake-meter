import json
import os
from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.datastore.context import ModbusSequentialDataBlock

# Lade die Konfigurationsdaten aus der JSON-Datei
def load_config():
    try:
        # Hole den aktuellen Benutzernamen
        user_name = os.getlogin()
        
        # Baue den Pfad zur config.json auf
        config_path = f"/home/{user_name}/fronius-fake-meter/config.json"

        # Öffne die config.json-Datei
        with open(config_path) as f:
            return json.load(f)
    except FileNotFoundError:
        print("Fehler: config.json nicht gefunden!")
        return None

# Erstelle die Modbus-Datenstruktur für den Server
def create_modbus_data(config):
    if config is None:
        return None

    # Hier definieren wir die "gefälschten" Werte, die du anpassen möchtest
    block = ModbusSequentialDataBlock(0, [
        config['modbus_ip'],  # Netzbezug (Beispiel)
        config['modbus_port'],  # Einspeisung (Beispiel)
        config['battery_max_charge'],  # Max. Batterieladung (Beispiel)
        config['battery_min_charge'],  # Min. Batterieladung (Beispiel)
        config['overshoot_watt'],  # Überschuss-Watt (Beispiel)
    ])

    # Erstelle den Modbus-Slave-Kontext
    store = ModbusSlaveContext(
        hr=block,  # Halregister (Register für kontinuierliche Daten)
        co=block,  # Coilregister (optional, wenn du Schaltbefehle brauchst)
    )
    context = ModbusServerContext(slaves=store, single=True)
    return context

# Starte den Modbus-Server auf Port 502
def start_modbus_server():
    print("Lade Konfiguration...")
    config = load_config()

    # Falls die Konfiguration nicht geladen werden konnte, beende das Programm
    if config is None:
        print("Server kann nicht gestartet werden. Konfiguration fehlt.")
        return

    print("Starte Modbus-Server auf Port 502...")
    context = create_modbus_data(config)

    # Starte den Modbus TCP-Server auf dem Pi
    if context:
        StartTcpServer(context, address=("0.0.0.0", 502))

if __name__ == "__main__":
    start_modbus_server()
