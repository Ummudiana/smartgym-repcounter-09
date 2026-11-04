import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import pickle

# 1. DATASET (Data Latih)
# Jeda waktu dalam detik. 
# 0.5 - 1.5 detik = Cepat (0 / NORMAL)
# 2.0 - 5.0 detik = Lambat (1 / FATIGUE)
data = {
    'jeda_waktu': [0.5, 0.8, 1.0, 1.2, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0],
    'status':      [0,   0,   0,   0,   0,   1,   1,   1,   1,   1,   1,   1] 
}

df = pd.DataFrame(data)

# 2. LATIH MODEL AI (Supervised Learning)
X = df[['jeda_waktu']] 
y = df['status']       

# Menggunakan Decision Tree
model = DecisionTreeClassifier()
model.fit(X, y)

print("AI berhasil dilatih!")

# 3. SIMPAN MODEL
with open('model_fatigue.pkl', 'wb') as file:
    pickle.dump(model, file)
    
print("Model AI disimpan sebagai 'model_fatigue.pkl'")