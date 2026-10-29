import paho.mqtt.client as mqtt
from flask import Flask, render_template, jsonify
import json
from threading import Thread

app = Flask(__name__)

# --- 1. PENGATURAN ---
PROJECT_ID = "smartgym_kelompok_09" # GANTI DENGAN NAMA KELOMPOKMU (Harus sama dengan HP)
MQTT_HOST = "broker.hivemq.com"
MQTT_PORT = 1883
TOPIC_TELEMETRY = f"{PROJECT_ID}/edge1/telemetry"

# Menyimpan data sementara di memori laptop
latest_data = {"reps": 0, "status": "WAITING", "history": []}

# --- 2. FUNGSI MQTT (Menerima data dari HP) ---
def on_connect(client, userdata, flags, rc):
    print("Berhasil terhubung ke MQTT Broker!")
    client.subscribe(TOPIC_TELEMETRY)

def on_message(client, userdata, msg):
    global latest_data
    # Mengubah pesan JSON dari HP menjadi format Python
    data = json.loads(msg.payload.decode())
    
    # Update data terbaru
    latest_data["reps"] = data["reps"]
    latest_data["status"] = data["status"]
    
    # Simpan riwayat angka repetisi untuk grafik (maksimal 20 data)
    latest_data["history"].append(data["reps"])
    if len(latest_data["history"]) > 20:
        latest_data["history"].pop(0)
        
    print(f"Data masuk: Reps={data['reps']}, Status={data['status']}")

# --- 3. FUNGSI WEB (Menampilkan ke Browser) ---
@app.route('/')
def index():
    # Menampilkan file index.html
    return render_template('index.html')

@app.route('/data')
def get_data():
    # Mengirim data terbaru ke HTML dalam bentuk JSON
    return jsonify(latest_data)

# --- 4. MENJALANKAN PROGRAM ---
if __name__ == '__main__':
    # Setup MQTT
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    
    # Jalankan MQTT di background (agar tidak memblokir web)
    t = Thread(target=client.loop_forever)
    t.daemon = True
    t.start()
    
    # Jalankan Web Server Flask
    print("Dashboard berjalan di: http://127.0.0.1:5000")
    app.run(debug=True, use_reloader=False)