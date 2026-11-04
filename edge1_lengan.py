import subprocess
import json
import time
import math
import paho.mqtt.client as mqtt

PROJECT_ID = "smartgym_kelompok_09" 
MQTT_HOST = "broker.hivemq.com"
MQTT_PORT = 1883
TOPIC_TELEMETRY = f"{PROJECT_ID}/edge1/telemetry"
TOPIC_ALERT = f"{PROJECT_ID}/alerts"

# KITA TURUNKAN AGAR LEBIH MUDAH TERDETEKSI
THRESHOLD_ACCEL = 9.0  
FATIGUE_THRESHOLD = 0.15 # Cukup melambat 15% saja sudah dianggap lelah

def get_sensor_data():
    try:
        # Kita percepat pembacaan sensornya
        output = subprocess.run(
            ["termux-sensor", "-s", "accelerometer,gyroscope", "-n", "1"],
            capture_output=True, text=True, timeout=5
        ).stdout
        data = json.loads(output)
        
        accel_key = next((k for k in data if "Accelerometer" in k), None)
        if accel_key:
            ax, ay, az = data[accel_key]["values"][:3]
        else:
            ax, ay, az = 0, 0, 0

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
    last_rep_time = time.time()
    
    buffer_magnitude = []
    dynamic_threshold = 10.0
    
    print("Mulai membaca sensor. Lakukan Push-up/Squat...")
    
    try:
        while True:
            (ax, ay, az), (gx, gy, gz) = get_sensor_data()
            magnitude = math.sqrt(ax**2 + ay**2 + az**2)
            
            # 1. KALIBRASI OTOMATIS
            if len(buffer_magnitude) < 20:
                buffer_magnitude.append(magnitude)
                if len(buffer_magnitude) == 20:
                    rata_diam = sum(buffer_magnitude) / 20
                    dynamic_threshold = rata_diam + 1.5 # Diturunkan dari 2.0 agar lebih sensitif
                    print(f"Kalibrasi selesai. Batas gerak: {dynamic_threshold:.2f}")
                time.sleep(0.05)
                continue
            
            # 2. DETEKSI GERAKAN
            if magnitude > dynamic_threshold and not is_peak:
                is_peak = True
                rep_count += 1
                print(f"Repetisi ke-{rep_count} terdeteksi! (Mag: {magnitude:.2f})")
                
                current_time = time.time()
                time_diff = current_time - last_rep_time
                last_rep_time = current_time
                
                rotation_speeds.append(time_diff)
                
                status = "NORMAL"
                if len(rotation_speeds) >= 4:
                    awal = sum(rotation_speeds[:2]) / 2
                    akhir = sum(rotation_speeds[-2:]) / 2
                    
                    # Cek Kelelahan (Kita ubah logikanya pakai FATIGUE_THRESHOLD)
                    if awal > 0 and ((akhir - awal) / awal) > FATIGUE_THRESHOLD: 
                        status = "FATIGUE"
                        print("⚠️ KELELAHAN TERDETEKSI! (Gerakan melambat)")
                        client.publish(TOPIC_ALERT, json.dumps({"status": "WARNING", "message": "Kelelahan! Segera istirahat."}), qos=1)
                
                payload = {"device_id": "edge1", "reps": rep_count, "status": status, "timestamp": time.time()}
                client.publish(TOPIC_TELEMETRY, json.dumps(payload), qos=1)
            
            # 3. RESET PUNCAK
            elif magnitude < (dynamic_threshold - 0.5) and is_peak:
                is_peak = False 
                
            # DIPERCEPAT DARI 0.05 JADI 0.02 (50 kali per detik)
            time.sleep(0.02) 
            
    except KeyboardInterrupt:
        print("Program dihentikan.")
        client.loop_stop()

if __name__ == "__main__":
    main()