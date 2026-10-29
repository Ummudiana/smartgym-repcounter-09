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
        print("🚨 MENERIMA ALERT KELELAHAN! Bunyikan alarm...")
        
        # 1. Coba Getar (kalau berhasil, bagus)
        subprocess.run(["termux-vibrate", "-d", "1000"])
        
        # 2. Munculkan Notifikasi
        subprocess.run(["termux-notification", "--title", "🚨 ALARM KELELAHAN!", "--content", data.get("message", "")])
        
        # 3. BUNYIKAN SUARA ALARM (Ini yang paling penting!)
        subprocess.run(["termux-tts-speak", "Peringatan! Anda sudah kelelahan, silakan istirahat!"])