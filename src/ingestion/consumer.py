import json
import paho.mqtt.client as mqtt
import psycopg2
from datetime import datetime

# Configurări MQTT
MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883
MQTT_TOPIC = "fleet/telemetry"

# Configurări PostgreSQL (din .env-ul tău)
DB_HOST = "127.0.0.1"
DB_PORT = "5432"
DB_USER = "fleet"
DB_PASS = "1234"
DB_NAME = "postgres"

# Conectarea la baza de date
try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        dbname=DB_NAME
    )
    conn.autocommit = True
    cursor = conn.cursor()
    print("Conectat cu succes la PostgreSQL!")
except Exception as e:
    print(f"Eroare la conectarea la baza de date: {e}")
    exit(1)

# Funcția care se declanșează la fiecare mesaj nou primit din MQTT
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))

        v_id = payload["vehicle_id"]
        trip_id = payload.get("trip_id")
        timestamp = payload["timestamp"]
        run_time = payload.get("engine_run_time_s")
        speed = payload["vehicle_speed_kmh"]
        rpm = payload["engine_rpm"]
        throttle = payload.get("throttle_pct")
        load = payload.get("engine_load_pct")
        coolant = payload.get("coolant_temp_c")

        insert_query = """
            INSERT INTO obd_telemetry
            (vehicle_id, trip_id, timestamp, engine_run_time_s, vehicle_speed_kmh,
             engine_rpm, throttle_pct, engine_load_pct, coolant_temp_c)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(insert_query, (v_id, trip_id, timestamp, run_time, speed,
                                      rpm, throttle, load, coolant))
        print(f"[SALVAT] {trip_id} | {run_time}s | {speed} km/h | {rpm} RPM")

    except Exception as e:
        print(f"[EROARE] Procesare mesaj eșuată: {e}")
    except Exception as e:
        print(f"[EROARE] Procesare mesaj eșuată: {e}")

# Setăm clientul MQTT
client = mqtt.Client("Postgres_Ingestion_Service")
client.on_message = on_message

print("Se conectează la MQTT...")
client.connect(MQTT_BROKER, MQTT_PORT)
client.subscribe(MQTT_TOPIC)

print("Consumatorul ascultă mesaje... (Apasă Ctrl+C pentru a opri)")
client.loop_forever()