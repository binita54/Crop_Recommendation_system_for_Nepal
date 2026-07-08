import pickle
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

FEATURE_COLS = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

df = pd.read_csv("Nepal_crop_recommendation_zoned.csv")

X = df[FEATURE_COLS]
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)

print(f"Dataset size: {len(df)} rows, {df['label'].nunique()} crop classes, {df['zone'].nunique()} zones")
print(f"Train size: {len(X_train)}  |  Test size: {len(X_test)}")
print(f"Test Accuracy: {acc:.4f}\n")
print("Classification Report:\n")
print(classification_report(y_test, y_pred))

bundle = {"model": model, "feature_cols": FEATURE_COLS}
with open("Crop_recommendation_RF.pkl", "wb") as f:
    pickle.dump(bundle, f)

print("Model saved to: Crop_recommendation_RF.pkl")
