import pickle

# Memanggil model AI yang sudah dilatih
with open('model_fatigue.pkl', 'rb') as file:
    ai_model = pickle.load(file)

print("=== TES AI SMARTGYM ===")

# Kita coba tebak beberapa jeda waktu
tes_jeda = [0.6, 1.0, 2.5, 4.0]

for jeda in tes_jeda:
    # AI memprediksi
    prediksi = ai_model.predict([[jeda]])[0]
    
    if prediksi == 1:
        hasil = "FATIGUE (Lelah)"
    else:
        hasil = "NORMAL (Cepat)"
        
    print(f"Jeda {jeda} detik -> AI memprediksi: {hasil}")