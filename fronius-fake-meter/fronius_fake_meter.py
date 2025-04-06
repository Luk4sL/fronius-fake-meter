import json
import os
import time
from pymodbus.client.sync import ModbusTcpClient

# Funktion zum Laden der Konfiguration basierend auf dem Benutzernamen
def load_config():
    username = os.getenv("USER")  # Benutzername (z.B. LIND, STANGL, etc.)
    config_path = f"/home/pi/fronius-fake-meter/config/{username}.json"
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

# Modbus-Verbindung herstellen
client = ModbusTcpClient(modbus_ip, port=modbus_port)
client.connect()

# Beispielhafte Modbus-Abfrage (hier wird der Batteriestand abgefragt)
def read_battery_status():
    result = client.read_holding_registers(0, 2, unit=modbus_slave_id)
    return result.registers[0]  # Angenommene Registerposition für den Batteriestatus

# Weitere Modbus-Funktionen können hier hinzugefügt werden

while True:
    battery_status = read_battery_status()
    print(f"Batteriestatus: {battery_status}%")
    
    # Logik zur Steuerung der Batterie (z.B. Lade- oder Entladebedingungen)
    if battery_status > battery_max:
        print(f"Maximale Batteriekapazität erreicht, überschüssige Energie umkehren.")
    elif battery_status < battery_min:
        print(f"Batterie unter Mindestkapazität, Energie laden.")
    
    # 20 Sekunden warten, bevor die nächste Abfrage erfolgt
    time.sleep(20)

client.close()
