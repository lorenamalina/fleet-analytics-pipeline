import csv, glob, json, os, re, time
from datetime import datetime
import paho.mqtt.client as mqtt

BROKER = "127.0.0.1"
PORT = 1883
TOPIC = "fleet/telemetry"
DATA_GLOB = "src/collector/dataset_obd/live*.csv"
SLEEP_S = 0.005  # timpul vine din log, deci ritmul trimiterii nu afecteaza analiza

def to_float(v):
    try:
        return float(v) if v is not None and v.strip() != '' else None
    except ValueError:
        return None

def natural(p):
    return int(re.findall(r'\d+', os.path.basename(p))[0])

def find(cols, key):
    return next((c for c in cols if key in c.upper()), None)

def main():
    client = mqtt.Client("OBD_Streamer")
    client.connect(BROKER, PORT)
    client.loop_start()
    sent = {}
    for path in sorted(glob.glob(DATA_GLOB), key=natural):
        trip = os.path.basename(path).replace('.csv', '')
        with open(path, newline='') as f:
            rd = csv.DictReader(f)
            c_t = find(rd.fieldnames, 'ENGINE_RUN')
            c_v = find(rd.fieldnames, 'VEHICLE_SPEED')
            c_r = find(rd.fieldnames, 'ENGINE_RPM')
            c_th = find(rd.fieldnames, 'THROTTLE ()')
            c_ld = find(rd.fieldnames, 'ENGINE_LOAD')
            c_ct = find(rd.fieldnames, 'COOLANT')
            n = 0
            for row in rd:
                speed = to_float(row.get(c_v)) or 0.0
                rpm = to_float(row.get(c_r)) or 0.0
                if speed == 0.0 and rpm == 0.0:
                    continue
                payload = {
                    "vehicle_id": "TOYOTA_ETIOS_01",
                    "trip_id": trip,
                    "timestamp": datetime.utcnow().isoformat(),
                    "engine_run_time_s": to_float(row.get(c_t)) or 0.0,
                    "vehicle_speed_kmh": speed,
                    "engine_rpm": rpm,
                    "throttle_pct": to_float(row.get(c_th)),
                    "engine_load_pct": to_float(row.get(c_ld)),
                    "coolant_temp_c": to_float(row.get(c_ct)),
                }
                client.publish(TOPIC, json.dumps(payload), qos=1)
                n += 1
                time.sleep(SLEEP_S)
        sent[trip] = n
        print(f"{trip}: {n} mesaje trimise")
    print("Total:", sum(sent.values()))
    time.sleep(2)
    client.loop_stop()
    client.disconnect()

if __name__ == "__main__":
    main()
