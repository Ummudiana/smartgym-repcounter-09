import paho.mqtt.client as mqtt
import json
import subprocess

PROJECT_ID = "smartgym_kelompok_09" # SAMAKAN DENGAN HP 1
MQTT_HOST = "broker.hivemq.com"
MQTT_PORT = 1883
TOPIC_ALERT = f"{PROJECT_ID}/alerts"

def on_connect(client, userdata, flags, rc):
    print(f"Terhubung ke MQTT. Kode: {rc}")
    client.subscribe(TOPIC_ALERT)

def on_message(client, userdata, msg):
    print(f"Pesan masuk: {msg.payload.decode()}")
    data = json.loads(msg.payload.decode())
    if data.get("status") == "WARNING":
        print("🚨 MENERIMA ALERT KELELAHAN! Bergetar...")
        subprocess.run(["termux-vibrate", "-d", "2000"])
        subprocess.run(["termux-notification", "--title", "SmartGym", "--content", data.get("message", "")])

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print("Menghubungkan ke MQTT...")
client.connect(MQTT_HOST, MQTT_PORT, 60)
client.loop_forever()