import os
import paho.mqtt.client as mqtt
import psycopg2

from common.telemetry import parse_message

MQTT_BROKER = os.environ.get("MQTT_BROKER", "127.0.0.1")
MQTT_PORT = int(os.environ.get("MQTT_PORT", "1883"))
MQTT_TOPIC = os.environ.get("MQTT_TOPIC", "fleet/telemetry")
TABLE = os.environ.get("TARGET_TABLE", "obd_telemetry")
CLIENT_ID = os.environ.get("MQTT_CLIENT_ID", "Postgres_Ingestion_Service")

DB_HOST = os.environ.get("POSTGRES_HOST", "127.0.0.1")
DB_PORT = os.environ.get("POSTGRES_PORT", "5432")
DB_USER = os.environ["POSTGRES_USER"]
DB_PASS = os.environ["POSTGRES_PASSWORD"]
DB_NAME = os.environ["POSTGRES_DB"]

INSERT_QUERY = """
    INSERT INTO {table}
    (vehicle_id, trip_id, timestamp, engine_run_time_s, vehicle_speed_kmh,
     engine_rpm, throttle_pct, engine_load_pct, coolant_temp_c)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
"""


def connect_db():
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, user=DB_USER,
                            password=DB_PASS, dbname=DB_NAME)
    conn.autocommit = True
    return conn


def on_message(client, userdata, msg):
    try:
        p = parse_message(msg.payload)
        userdata["cursor"].execute(INSERT_QUERY.format(table=TABLE), (
            p["vehicle_id"], p.get("trip_id"), p["timestamp"],
            p.get("engine_run_time_s"), p["vehicle_speed_kmh"],
            p["engine_rpm"], p.get("throttle_pct"),
            p.get("engine_load_pct"), p.get("coolant_temp_c"),
        ))
        print(f"[SALVAT] {p.get('trip_id')} | {p.get('engine_run_time_s')}s")
    except Exception as e:
        print(f"[EROARE] Procesare mesaj esuata: {e}")


def main():
    conn = connect_db()
    print("Conectat la PostgreSQL")
    # clean_session=False: brokerul pastreaza mesajele QoS 1 cat timp consumer-ul e oprit
    client = mqtt.Client(CLIENT_ID, clean_session=False,
                         userdata={"cursor": conn.cursor()})
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT)
    client.subscribe(MQTT_TOPIC, qos=1)
    print("Consumatorul asculta mesaje... (Ctrl+C pentru oprire)")
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("Oprit.")
        client.disconnect()


if __name__ == "__main__":
    main()
