import json
import mysql.connector
from paho.mqtt import client as mqtt_client

# MQTT Broker
BROKER = "test.mosquitto.org"
PORT = 1883
TOPICS = ["uts/suhu", "uts/kelembapan", "uts/lux"]

# Tempat nyimpen data sementara
buffer_data = {
    "suhu": None,
    "humidity": None,
    "lux": None
}

# Koneksi ke database
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="db_sensor_iot"
    )

# Ketika ada message masuk
def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()

    print(f"[MQTT] {topic}: {payload}")

    if topic == "uts/suhu":
        buffer_data["suhu"] = float(payload)
    elif topic == "uts/kelembapan":
        buffer_data["humidity"] = float(payload)
    elif topic == "uts/lux":
        buffer_data["lux"] = int(float(payload))

    # Jika semua data ada → simpan ke DB
    if all(buffer_data.values()):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO data_sensor (suhu, humidity, lux) VALUES (%s, %s, %s)",
            (buffer_data["suhu"], buffer_data["humidity"], buffer_data["lux"])
        )
        conn.commit()
        cur.close()
        conn.close()

        print("[DB] Data inserted:", buffer_data)

        # reset buffer
        buffer_data["suhu"] = None
        buffer_data["humidity"] = None
        buffer_data["lux"] = None


def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker")
    for topic in TOPICS:
        client.subscribe(topic)
        print("Subscribed to:", topic)


# Hapus baris ini
# from paho.mqtt.client import CallbackAPIVersion 

def run_mqtt():
    client = mqtt_client.Client(
        client_id="Backend_Listener"
        # Hapus baris ini: callback_api_version=CallbackAPIVersion.v1 
    )
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.loop_forever()

if __name__ == "__main__":
    run_mqtt()
