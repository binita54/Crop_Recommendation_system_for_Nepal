"""
Build the BEST achievable Nepal crop-recommendation model and save Crop_recommendation_RF.pkl.

Reality (document in report):
  - No public dataset is both REAL and complete for Nepal's 15 crops.
  - Kaggle "Crop Recommendation Dataset" is REAL but missing 8 Nepal crops
    (wheat, potato, sugarcane, barley, ginger, millet, mustard, soybean).
  - NARC soil API is REAL but gives location-independent crop labels (unusable).
So we MERGE:
  - 7 Nepal crops that exist in Kaggle  -> trained on REAL data
  - 8 Nepal-only crops                  -> trained on synthetic zoned data
Result: 15 Nepal crops, working model, 7 of them real. Future work: collect
real Nepal soil/crop data for the remaining 8 crops.
"""
import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

HERE = os.path.dirname(os.path.abspath(__file__))
FEATURE_COLS = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

NEPAL_15 = {"banana", "barley", "blackgram", "chickpea", "ginger", "lentil",
            "maize", "mango", "millet", "mustard", "potato", "rice",
            "soybean", "sugarcane", "wheat"}
REAL_CROPS = NEPAL_15 & {"apple", "banana", "blackgram", "chickpea", "coconut",
                         "coffee", "cotton", "grapes", "jute", "kidneybeans",
                         "lentil", "maize", "mango", "mothbeans", "mungbean",
                         "muskmelon", "orange", "papaya", "pigeonpeas",
                         "pomegranate", "rice", "watermelon"}

# --- real Kaggle rows for the overlapping Nepal crops ---
k = pd.read_csv(os.path.join(HERE, "Crop_recommendation_kaggle.csv"))
k = k.rename(columns={"Nitrogen": "N", "Phosphorus": "P", "Potassium": "K",
                      "Temperature": "temperature", "Humidity": "humidity",
                      "pH_Value": "ph", "Rainfall": "rainfall", "Crop": "label"})
k["label"] = k["label"].str.lower()
k = k[k["label"].isin(NEPAL_15)][FEATURE_COLS + ["label"]]
print(f"Real (Kaggle) rows kept: {len(k)} -> crops: {sorted(k['label'].unique())}")

# --- synthetic zoned rows for all 15 Nepal crops ---
z = pd.read_csv(os.path.join(HERE, "data", "Nepal_crop_recommendation_zoned.csv"))
z = z[z["label"].isin(NEPAL_15)][FEATURE_COLS + ["label"]]
print(f"Synthetic (zoned) rows kept: {len(z)} -> crops: {sorted(z['label'].unique())}")

df = pd.concat([k, z], ignore_index=True)
print(f"\nMERGED: {len(df)} rows, {df['label'].nunique()} crops")

X = df[FEATURE_COLS]
y = df["label"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
print(f"\nTest accuracy: {accuracy_score(y_test, y_pred):.4f}\n")
print(classification_report(y_test, y_pred, zero_division=0))

import pickle
with open(os.path.join(HERE, "Crop_recommendation_RF.pkl"), "wb") as f:
    pickle.dump({"model": model, "feature_cols": FEATURE_COLS}, f)
print("Model saved to Crop_recommendation_RF.pkl")
