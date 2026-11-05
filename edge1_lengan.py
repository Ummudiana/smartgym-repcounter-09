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
    
    print("HP 1 Mode Streaming. Mulai membaca sensor...")
    
    process = subprocess.Popen(
        ["termux-sensor", "-s", "accelerometer", "-d", "20", "-n", "100000"],
        stdout=subprocess.PIPE, text=True, bufsize=1
    )
    
    try:
        buffer = ""
        for line in iter(process.stdout.readline, ''):
            buffer += line
            
            if buffer.strip().endswith('}'):
                try:
                    data = json.loads(buffer)
                    buffer = "" 
                    
                    accel_key = next((k for k in data if "Accelerometer" in k), None)
                    if accel_key:
                        ax, ay, az = data[accel_key]["values"][:3]
                        magnitude = math.sqrt(ax**2 + ay**2 + az**2)
                        
                        # --- LANGKAH 2: KALIBRASI 50 DATA ---
                        if len(buffer_magnitude) < 50:
                            buffer_magnitude.append(magnitude)
                            if len(buffer_magnitude) == 50:
                                rata_diam = sum(buffer_magnitude) / 50
                                dynamic_threshold = rata_diam + 1.5 
                                print(f"Kalibrasi selesai. Batas: {dynamic_threshold:.2f}")
                                last_rep_time = time.time() 
                            continue
                        
                        # --- LANGKAH 3 & 4: DETEKSI REPETISI & JEDA ---
                        if magnitude > dynamic_threshold and not is_peak and (time.time() - last_rep_time) > 0.5:
                            is_peak = True
                            rep_count += 1
                            
                            current_time = time.time()
                            time_diff = current_time - last_rep_time
                            last_rep_time = current_time
                            
                            print(f"Rep-{rep_count} | Jeda Akurat: {time_diff:.2f}s")
                            
                            payload = {
                                "device_id": "edge1", 
                                "reps": rep_count, 
                                "jeda_waktu": time_diff, 
                                "timestamp": time.time()
                            }
                            client.publish(TOPIC_TELEMETRY, json.dumps(payload), qos=1)
                        
                        elif magnitude < (dynamic_threshold - 0.5) and is_peak:
                            is_peak = False 
                            
                except json.JSONDecodeError:
                    pass 
                
    except KeyboardInterrupt:
        print("Program dihentikan.")
        process.terminate()
        client.loop_stop()

if __name__ == "__main__":
    main()