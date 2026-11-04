import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import pickle

# DATA LATIH BARU (Lebih Toleran)
data = {
    'jeda_waktu': [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0],
    'status':      [0,   0,   0,   0,   0,   1,   1,   1,   1,   1] 
}

df = pd.DataFrame(data)
X = df[['jeda_waktu']] 
y = df['status']       

model = DecisionTreeClassifier()
model.fit(X, y)

print("AI berhasil dilatih ulang dengan data baru!")

with open('model_fatigue.pkl', 'wb') as file:
    pickle.dump(model, file)
    
print("Model AI disimpan sebagai 'model_fatigue.pkl'")