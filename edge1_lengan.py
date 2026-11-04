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
        ["termux-sensor", "-s", "accelerometer", "-n", "100000"],
        stdout=subprocess.PIPE, text=True
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
                        
                        if len(buffer_magnitude) < 15:
                            buffer_magnitude.append(magnitude)
                            if len(buffer_magnitude) == 15:
                                rata_diam = sum(buffer_magnitude) / 15
                                dynamic_threshold = rata_diam + 1.5 
                                print(f"Kalibrasi selesai. Batas: {dynamic_threshold:.2f}")
                                last_rep_time = time.time() 
                            continue
                        
                        if magnitude > dynamic_threshold and not is_peak:
                            is_peak = True
                            rep_count += 1
                            
                            # --- TRIK WAKTU (ANTI TERSENDAT) ---
                            # Kita paksa jeda maksimal 2.5 detik agar tidak kacau
                            current_time = time.time()
                            time_diff = current_time - last_rep_time
                            
                            # Jika HP tersendat dan jeda > 2.5 detik, kita paksa anggap 1.0 detik
                            # (Asumsi: orang gerak cepat jedanya ~1 detik)
                            if time_diff > 2.5:
                                time_diff = 1.0 
                            
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