import paho.mqtt.client as mqtt
from flask import Flask, render_template, jsonify
import json
from threading import Thread
import pickle # Memanggil AI

app = Flask(__name__)

PROJECT_ID = "smartgym_kelompok_09"
MQTT_HOST = "broker.hivemq.com"
MQTT_PORT = 1883
TOPIC_TELEMETRY = f"{PROJECT_ID}/edge1/telemetry"
TOPIC_ALERT = f"{PROJECT_ID}/alerts"

# MEMANGGIL MODEL AI DI LAPTOP
with open('model_fatigue.pkl', 'rb') as file:
    ai_model = pickle.load(file)

latest_data = {"reps": 0, "status": "WAITING", "history": []}

def on_connect(client, userdata, flags, rc):
    print("Berhasil terhubung ke MQTT Broker!")
    client.subscribe(TOPIC_TELEMETRY)

def on_message(client, userdata, msg):
    global latest_data
    data = json.loads(msg.payload.decode())
    
    reps = data["reps"]
    jeda = data.get("jeda_waktu", 0)
    print(f"DEBUG: Rep-{reps} | Jeda Terbaca: {jeda:.3f} detik")
    status = "NORMAL"
    
    # LAPTOP MELAKUKAN PREDIKSI AI
    if reps > 2:
        prediksi = ai_model.predict([[jeda]])[0]
        if prediksi == 1:
            status = "FATIGUE"
            print(f"Rep {reps} | Jeda {jeda:.2f}s | 🤖 AI: KELELAHAN!")
            # Kirim ALARM ke HP 2
            client.publish(TOPIC_ALERT, json.dumps({"status": "WARNING", "message": "AI mendeteksi kelelahan!"}), qos=1)
        else:
            print(f"Rep {reps} | Jeda {jeda:.2f}s | 🤖 AI: NORMAL")
    
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