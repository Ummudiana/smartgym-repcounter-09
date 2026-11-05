import paho.mqtt.client as mqtt
from flask import Flask, render_template, jsonify
import json
from threading import Thread
import pickle  # Memanggil AI

app = Flask(__name__)

PROJECT_ID = "smartgym_kelompok_09"
MQTT_HOST = "broker.hivemq.com"
MQTT_PORT = 1883
TOPIC_TELEMETRY = f"{PROJECT_ID}/edge1/telemetry"
TOPIC_ALERT = f"{PROJECT_ID}/alerts"

# MEMANGGIL MODEL AI DI LAPTOP
with open('model_fatigue.pkl', 'rb') as file:
    ai_model = pickle.load(file)

# Variabel untuk menyimpan riwayat (untuk hitung konsistensi & lonjakan)
riwayat_jeda = []
label_map = {0: "NORMAL", 1: "FATIGUE", 2: "GAP_SENSOR"}

latest_data = {"reps": 0, "status": "WAITING", "history": []}

def on_connect(client, userdata, flags, rc):
    print("Berhasil terhubung ke MQTT Broker!")
    client.subscribe(TOPIC_TELEMETRY)

def on_message(client, userdata, msg):
    global latest_data, riwayat_jeda
    data = json.loads(msg.payload.decode())
    
    reps = data["reps"]
    jeda = data.get("jeda_waktu", 0)
    print(f"DEBUG: Rep-{reps} | Jeda Terbaca: {jeda:.3f} detik")
    
    status = "NORMAL"  # Default status
    
    # LAPTOP MELAKUKAN PREDIKSI AI (Mulai Repetisi ke-2)
    if reps >= 2:
        riwayat_jeda.append(jeda)
        riwayat_jeda = riwayat_jeda[-3:]  # Simpan 3 data terakhir saja
        
        if len(riwayat_jeda) >= 2:
            # 1. Hitung Rata-rata dan Konsistensi (Standar Deviasi)
            rata_rata = sum(riwayat_jeda) / len(riwayat_jeda)
            konsistensi = sum(abs(x - rata_rata) for x in riwayat_jeda) / len(riwayat_jeda)
            
            # 2. Hitung Lonjakan
            jeda_sebelumnya = riwayat_jeda[-2]
            lonjakan = jeda / jeda_sebelumnya if jeda_sebelumnya > 0 else 1.0
            
            # 3. Filter GAP_SENSOR (Anti Ngadat)
            if lonjakan > 3.0 or konsistensi > 2.0:
                status = "GAP_SENSOR"
                print(f"Rep {reps} | Jeda {jeda:.2f}s | ⚠️ GAP_SENSOR (Data dibuang dari memori)")
                riwayat_jeda.pop() # Buang data ngadat agar memori tetap bersih
            else:
                # 4. Prediksi ke AI (Hanya jika data aman)
                fitur = [[jeda, konsistensi, lonjakan]]
                hasil_angka = ai_model.predict(fitur)[0]
                status = label_map[hasil_angka]
                
                print(f"Rep {reps} | Jeda {jeda:.2f}s | Konsisten: {konsistensi:.2f} | Lonjakan: {lonjakan:.2f} | 🤖 AI: {status}")
                
                # Kirim Alarm ke HP 2 jika FATIGUE
                if hasil_angka == 1:
                    client.publish(TOPIC_ALERT, json.dumps({"status": "WARNING", "message": "AI mendeteksi kelelahan asli!"}), qos=1)
                elif hasil_angka == 2:
                    riwayat_jeda.pop()
                    print("   -> (Sensor HP 1 tersendat, data diabaikan)")
    
    latest_data["reps"] = reps
    latest_data["status"] = status
    latest_data["history"].append(reps)
    if len(latest_data["history"]) > 20:
        latest_data["history"].pop(0)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    return jsonify(latest_data)

if __name__ == '__main__':
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    t = Thread(target=client.loop_forever)
    t.daemon = True
    t.start()
    print("Dashboard + AI berjalan di: http://127.0.0.1:5000")
    app.run(debug=True, use_reloader=False)