import subprocess
import json
import time
import math
import paho.mqtt.client as mqtt

PROJECT_ID = "smartgym_kelompok_09" # GANTI DENGAN ID KELOMPOKMU
MQTT_HOST = "broker.hivemq.com"
MQTT_PORT = 1883
TOPIC_TELEMETRY = f"{PROJECT_ID}/edge1/telemetry"
TOPIC_ALERT = f"{PROJECT_ID}/alerts"

THRESHOLD_ACCEL = 7.0  
FATIGUE_THRESHOLD = 0.30 

def get_sensor_data():
    try:
        output = subprocess.run(
            ["termux-sensor", "-s", "accelerometer,gyroscope", "-n", "1"],
            capture_output=True, text=True, timeout=5
        ).stdout
        data = json.loads(output)
        
        # Cari Accelerometer (Menggunakan LSM6DSVTR)
        accel_key = next((k for k in data if "Accelerometer" in k), None)
        if accel_key:
            ax, ay, az = data[accel_key]["values"][:3]
        else:
            ax, ay, az = 0, 0, 0

        # Cari Gyroscope (Jika tidak ada, isi 0 agar tidak error)
        gyro_key = next((k for k in data if "Gyroscope" in k), None)
        if gyro_key:
            gx, gy, gz = data[gyro_key]["values"][:3]
        else:
            gx, gy, gz = 0, 0, 0 
            
        return (ax, ay, az), (gx, gy, gz)
    except Exception as e:
        return (0,0,0), (0,0,0)

def on_connect(client, userdata, flags, rc):
    print(f"Terhubung ke MQTT Broker dengan kode: {rc}")

client = mqtt.Client()
client.on_connect = on_connect

def main():
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_start()
    rep_count = 0
    is_peak = False
    rotation_speeds = []
    print("Mulai membaca sensor. Lakukan Push-up/Squat...")
    try:
        while True:
            (ax, ay, az), (gx, gy, gz) = get_sensor_data()
            magnitude = math.sqrt(ax**2 + ay**2 + az**2)
            if magnitude > THRESHOLD_ACCEL and not is_peak:
                is_peak = True
                rep_count += 1
                print(f"Repetisi ke-{rep_count} terdeteksi!")
                rot_speed = math.sqrt(gx**2 + gy**2 + gz**2)
                rotation_speeds.append(rot_speed)
                status = "NORMAL"
                if len(rotation_speeds) >= 5:
                    awal = sum(rotation_speeds[:3]) / 3
                    akhir = sum(rotation_speeds[-3:]) / 3
                    if awal > 0 and ((awal - akhir) / awal) > FATIGUE_THRESHOLD:
                        status = "FATIGUE"
                        print("⚠️ KELELAHAN TERDETEKSI!")
                        client.publish(TOPIC_ALERT, json.dumps({"status": "WARNING", "message": "Kelelahan! Segera istirahat."}), qos=1)
                
                payload = {"device_id": "edge1", "reps": rep_count, "status": status, "timestamp": time.time()}
                client.publish(TOPIC_TELEMETRY, json.dumps(payload), qos=1)
            elif magnitude < THRESHOLD_ACCEL and is_peak:
                is_peak = False 
            time.sleep(0.1) 
    except KeyboardInterrupt:
        print("Program dihentikan.")
        client.loop_stop()

if __name__ == "__main__":
    main()