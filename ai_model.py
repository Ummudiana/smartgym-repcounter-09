import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import pickle

# 0=NORMAL, 1=FATIGUE, 2=GAP_SENSOR (HP tersendat)
data = {
    'jeda_waktu':  [0.8, 0.9, 1.0, 1.1, 1.2, 1.0, 0.9, 1.1,
                    2.5, 3.0, 3.5, 4.0, 4.2, 4.5,
                    3.5, 4.0, 5.0, 6.0],
    'konsistensi': [0.1, 0.1, 0.1, 0.1, 0.2, 0.1, 0.1, 0.2,
                    0.3, 0.4, 0.4, 0.5, 0.5, 0.5,
                    2.0, 2.5, 3.0, 3.5],
    'lonjakan':    [1.0, 1.1, 1.0, 1.0, 1.1, 1.0, 1.1, 1.0,
                    1.2, 1.3, 1.2, 1.3, 1.2, 1.3,
                    3.5, 4.0, 5.0, 4.5],
    'status':      [0, 0, 0, 0, 0, 0, 0, 0,
                    1, 1, 1, 1, 1, 1,
                    2, 2, 2, 2]
}

df = pd.DataFrame(data)
X = df[['jeda_waktu', 'konsistensi', 'lonjakan']]
y = df['status']

model = DecisionTreeClassifier(max_depth=3, random_state=42)
model.fit(X, y)

# Uji cepat model dengan 3 contoh
contoh = [
    ([1.0, 0.1, 1.0], "gerakan cepat normal"),
    ([4.0, 0.5, 1.2], "fatigue asli (melambat mulus)"),
    ([4.0, 3.0, 5.0], "HP tersendat (loncat ekstrem)"),
]
label_map = {0: "NORMAL", 1: "FATIGUE", 2: "GAP_SENSOR"}

print(" UJI MODEL BARU ")
for fitur, ket in contoh:
    hasil = model.predict([fitur])[0]
    print(f"  {fitur} -> {label_map[hasil]:10s} ({ket})")

with open('model_fatigue.pkl', 'wb') as f:
    pickle.dump(model, f)
print("\nModel 3-fitur disimpan sebagai 'model_fatigue.pkl'")