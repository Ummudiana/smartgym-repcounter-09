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

THRESHOLD_ACCEL = 9.0  

def get_sensor_data():
    try:
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
        return (ax, ay, az)
    except:
        return (0,0,0)

def on_connect(client, userdata, flags, rc):
    print(f"Terhubung ke MQTT. Kode: {rc}")

client = mqtt.Client()
client.on_connect = on_connect

def main():
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_start()
    
    rep_count = 0
    is_peak = False
    last_rep_time = time.time()
    buffer_magnitude = []
    dynamic_threshold = 10.0
    
    print("HP 1 Siap. Mengirim data jeda ke Laptop...")
    
    try:
        while True:
            (ax, ay, az) = get_sensor_data()
            magnitude = math.sqrt(ax**2 + ay**2 + az**2)
            
            # Kalibrasi
            if len(buffer_magnitude) < 20:
                buffer_magnitude.append(magnitude)
                if len(buffer_magnitude) == 20:
                    rata_diam = sum(buffer_magnitude) / 20
                    dynamic_threshold = rata_diam + 1.5 
                    print(f"Kalibrasi selesai. Batas: {dynamic_threshold:.2f}")
                    last_rep_time = time.time() # RESET TIMER setelah kalibrasi
                time.sleep(0.05)
                continue
            
            # Deteksi Gerakan
            if magnitude > dynamic_threshold and not is_peak:
                is_peak = True
                rep_count += 1
                
                current_time = time.time()
                time_diff = current_time - last_rep_time
                last_rep_time = current_time
                
                print(f"Rep-{rep_count} | Jeda: {time_diff:.2f}s")
                
                # Kirim data ke MQTT (Laptop yang akan memproses AI)
                payload = {
                    "device_id": "edge1", 
                    "reps": rep_count, 
                    "jeda_waktu": time_diff, 
                    "timestamp": time.time()
                }
                client.publish(TOPIC_TELEMETRY, json.dumps(payload), qos=1)
            
            elif magnitude < (dynamic_threshold - 0.5) and is_peak:
                is_peak = False 
                
            time.sleep(0.05) 
            
    except KeyboardInterrupt:
        print("Program dihentikan.")
        client.loop_stop()

if __name__ == "__main__":
    main()