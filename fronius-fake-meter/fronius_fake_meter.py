import json
import os
import time
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.server.sync import ModbusTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusContext
from pymodbus.datastore import ModbusSequentialDataBlock
import threading

# Funktion zum Laden der Konfiguration basierend auf dem Benutzernamen
def load_config():
    username = os.getenv("USER")  # Benutzername (z.B. LIND, STANGL, etc.)
    config_path = f"/home/{username}/fronius-fake-meter/config/{username}.json"
    with open(config_path, "r") as file:
        return json.load(file)

# Konfiguration laden
config = load_config()

# Parameter aus der Konfiguration extrahieren
modbus_ip = config.get("modbus_ip", "127.0.0.1")
modbus_port = config.get("modbus_port", 502)
modbus_slave_id = config.get("modbus_slave_id", 200)
battery_max = config.get("battery_max_charge", 90)
battery_min = config.get("battery_min_charge", 70)
overshoot_watt = config.get("overshoot_watt", 500)

# Modbus-Server für gefälschte Werte einrichten
def start_modbus_server():
    # Erstelle den Modbus-Datenstore (dies sind die gefälschten Werte)
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [0]*100),   # Digitale Eingänge (Dummy-Daten)
        co=ModbusSequentialDataBlock(0, [0]*100),   # Digitale Ausgänge
        hr=ModbusSequentialDataBlock(0, [500]*100), # Halte-Register (z.B. gefälschte Netzbezugswerte)
        ir=ModbusSequentialDataBlock(0, [0]*100),   # Eingangsregister
    )
    context = ModbusContext(slave_ids=store)
    server = ModbusTcpServer(context, port=502)
    print("Modbus TCP Server läuft auf Port 502 ...")
    server.serve_forever()

# Modbus-Client zum Abfragen von Batteriestatus
def read_battery_status():
    client = ModbusTcpClient(modbus_ip, port=modbus_port)
    client.connect()
    result = client.read_holding_registers(0, 2, unit=modbus_slave_id)
    battery_status = result.registers[0]  # Angenommene Registerposition für den Batteriestatus
    client.close()
    return battery_status

# Funktion für die Batterieüberwachung
def monitor_battery():
    while True:
        battery_status = read_battery_status()
        print(f"Batteriestatus: {battery_status}%")
        
        # Logik zur Steuerung der Batterie
        if battery_status > battery_max:
            print(f"Maximale Batteriekapazität erreicht, überschüssige Energie umkehren.")
        elif battery_status < battery_min:
            print(f"Batterie unter Mindestkapazität, Energie laden.")
        
        time.sleep(20)

# Starte den Modbus-Server in einem eigenen Thread
server_thread = threading.Thread(target=start_modbus_server)
server_thread.daemon = True
server_thread.start()

# Starte die Batterieüberwachung
monitor_battery()
