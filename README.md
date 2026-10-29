# 🏋️ SmartGym RepCounter - IoT-Based Workout Tracker

Proyek ini adalah sistem **Internet of Things (IoT)** yang dirancang untuk menghitung repetisi olahraga (seperti *push-up* atau *squat*) secara otomatis dan mendeteksi kelelahan otot (*fatigue*) secara *real-time*.

Sistem ini menggunakan **2 Edge Device (Smartphone Android)** yang berkomunikasi melalui protokol **MQTT** ke cloud, dan menampilkan data secara langsung melalui **Dashboard Web**.

## Anggota Kelompok 09
1. Amelia dini hanmarizqi   (24060125140126)
2. Ummu Diana Maghfiroh     (24060125140203)
3. Firstly Gisha Janatuka   (24060125120003)

## Latar Belakang & Masalah
Saat berolahraga mandiri di rumah, sering kali kita kehilangan fokus dan lupa menghitung repetisi yang sudah dilakukan. Selain itu, kita sulit menyadari kapan otot mulai mengalami kelelahan (postur mulai berantakan). Proyek ini hadir sebagai *personal trainer* digital untuk mengatasi masalah tersebut.

## Arsitektur Sistem
Sistem ini terdiri dari 3 komponen utama yang terhubung dalam satu jaringan:
1. **Edge 1 (HP di Lengan):** Bertindak sebagai pendeteksi gerakan. Membaca sensor *Accelerometer*, menghitung repetisi, dan mendeteksi kelelahan.
2. **Edge 2 (HP di Matras):** Bertindak sebagai penerima alarm. Akan berbunyi/bergetar jika Edge 1 mendeteksi kelelahan.
3. **Dashboard (Laptop):** Web server lokal (Flask) yang menampilkan grafik dan status secara *real-time*.

**Protokol Komunikasi:** MQTT (HiveMQ Public Broker) via Topik `smartgym_kelompok_09/...`

## Data Processing & Algoritma
Proyek ini memenuhi syarat minimal 2 jenis data processing:
1. **Peak Detection (Accelerometer):** Menghitung besaran *magnitude* (√x²+y²+z²). Gerakan naik-turun dideteksi dengan mencari lonjakan nilai yang melewati *Dynamic Threshold* (hasil kalibrasi otomatis saat HP diam).
2. **Time-Based Fatigue Detection:** Mengukur selisih waktu (*delta time*) antar repetisi. Jika jeda antar repetisi melambat lebih dari 50% dibandingkan repetisi awal, sistem akan menandai status **FATIGUE** dan mengirimkan sinyal peringatan via MQTT.

## Teknologi yang Digunakan
* **Edge Devices:** Android (Termux & Termux:API)
* **Bahasa Pemrograman:** Python 3
* **Library:** `paho-mqtt`, `flask`, `math`, `subprocess`, `json`
* **Cloud Broker:** HiveMQ (Public)
* **Dashboard:** HTML, CSS, JavaScript (Chart.js)

## Cara Menjalankan Proyek

### 1. Persiapan Edge Device (HP Android)
1. Install **F-Droid**, lalu install **Termux** dan **Termux:API** dari F-Droid.
2. Buka Termux, jalankan perintah:
   ```bash
   pkg update && pkg upgrade -y
   pkg install python git termux-api -y
   pip install paho-mqtt
   ```
3. Berikan izin (Permission) untuk Termux:API di pengaturan Android (Sensor & Getaran).

### 2. Clone Repositori
Lakukan di Termux (kedua HP) dan Laptop:
```bash
git clone https://github.com/Ummudiana/smartgym-repcounter-09.git
cd smartgym-repcounter-09
```

### 3. Menjalankan Sistem
* **Di Laptop (Dashboard):**
  ```bash
  pip install -r requirements.txt
  python dashboard.py
  ```
  Buka browser ke `http://127.0.0.1:5000`

* **Di HP 1 (Edge 1 - Lengan):**
  ```bash
  python edge1_lengan.py
  ```

* **Di HP 2 (Edge 2 - Matras):**
  ```bash
  python edge2_matras.py
  ```
