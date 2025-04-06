import json
import time
from pymodbus.server.sync import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer, ModbusBinaryFramer
from pymodbus.datastore import ModbusSequentialDataBlock
import threading
import requests

# Konfigurationsdatei laden
with open('config.json') as f:
    config = json.load(f)

modbus_ip = config.get("modbus_ip", "127.0.0.1")
modbus_port = config.get("modbus_port", 502)
modbus_slave_id = config.get("modbus_slave_id", 200)
battery_max = config.get("battery_max_charge", 90)
battery_min = config.get("battery_min_charge", 70)
overshoot_watt = config.get("overshoot_watt", 500)

# Dummy-Register für KEBA Wallbox (z. B. Überschuss in Watt)
store = ModbusSlaveContext(
    hr=ModbusSequentialDataBlock(0, [0]*100)
)
context = ModbusServerContext(slaves={modbus_slave_id: store}, single=False)

# Dummy: Batteriestand (in %) abrufen – HIER bitte echten HTTP/Modbus-Aufruf ersetzen!
def get_battery_soc():
    try:
        # Hier könntest du z. B. deine Wechselrichter-API abfragen
        # Beispiel: response = requests.get("http://ip/api")
        # return response.json()["battery_percent"]
        return 75  # Testwert
    except:
        return 75  # Fallback

# Dummy: Aktueller Überschuss vom Smart Meter – HIER ebenfalls echten Aufruf ersetzen!
def get_meter_power():
    try:
        # z. B. via Modbus auslesen
        return 1500  # Testwert (Überschuss in Watt)
    except:
        return 0

def update_loop():
    while True:
        battery_soc = get_battery_soc()
        raw_power = get_meter_power()
        adjusted_power = raw_power

        # Logik: Überschuss manipulieren je nach Batterie-SoC
        if battery_soc < battery_min:
            adjusted_power = max(0, raw_power - overshoot_watt)
        elif battery_soc > battery_max:
            adjusted_power = raw_power + overshoot_watt
        else:
            adjusted_power = 0  # Batterie wird weder be- noch entladen

        # In Modbus-Register schreiben
        # Register 0 = Überschuss
        context[modbus_slave_id].setValues(3, 0, [int(adjusted_power)])
        print(f"[INFO] SoC: {battery_soc} %, Power: {raw_power} W, Manipuliert: {adjusted_power} W")
        time.sleep(10)

# Hintergrund-Thread starten
thread = threading.Thread(target=update_loop)
thread.daemon = True
thread.start()

# Modbus TCP Server starten
identity = ModbusDeviceIdentification()
identity.VendorName = 'FakeMeter'
identity.ProductCode = 'FM'
identity.VendorUrl = 'https://github.com/Luk4sL'
identity.ProductName = 'Fronius Fake Meter'
identity.ModelName = 'v1.0'
identity.MajorMinorRevision = '1.0'

print(f"[INFO] Starte Modbus Server auf {modbus_ip}:{modbus_port}")
StartTcpServer(context, identity=identity, address=(modbus_ip, modbus_port))
