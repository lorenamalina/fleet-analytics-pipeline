import glob
import json
import os
import time

import paho.mqtt.client as mqtt

from common.telemetry import natural
from common.trip_reader import read_trip, trip_name

BROKER = os.environ.get("MQTT_BROKER", "127.0.0.1")
PORT = int(os.environ.get("MQTT_PORT", "1883"))
TOPIC = os.environ.get("MQTT_TOPIC", "fleet/telemetry")
DATA_GLOB = os.environ.get("DATA_GLOB", "src/collector/dataset_obd/live*.csv")
SLEEP_S = float(os.environ.get("SLEEP_S", "0.005"))  # timpul vine din log, ritmul nu afecteaza analiza


def main():
    client = mqtt.Client("OBD_Streamer")
    client.connect(BROKER, PORT)
    client.loop_start()
    sent = {}
    for path in sorted(glob.glob(DATA_GLOB), key=natural):
        trip = trip_name(path)
        n = 0
        for payload in read_trip(path):
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
