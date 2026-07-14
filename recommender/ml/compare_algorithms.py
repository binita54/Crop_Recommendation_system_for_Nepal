"""
Algorithm comparison for the crop-recommendation model.

Trains 5 classifiers on the SAME merged dataset (real Kaggle + synthetic zoned)
with the SAME train/test split, and reports accuracy so we can justify
choosing Random Forest. Scaled models (SVM, KNN, Logistic Regression) use a
StandardScaler fit on the training set only (no leakage).
"""
import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

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

# --- same merged data as train_hybrid_model.py ---
k = pd.read_csv(os.path.join(HERE, "Crop_recommendation_kaggle.csv"))
k = k.rename(columns={"Nitrogen": "N", "Phosphorus": "P", "Potassium": "K",
                      "Temperature": "temperature", "Humidity": "humidity",
                      "pH_Value": "ph", "Rainfall": "rainfall", "Crop": "label"})
k["label"] = k["label"].str.lower()
k = k[k["label"].isin(NEPAL_15)][FEATURE_COLS + ["label"]]
z = pd.read_csv(os.path.join(HERE, "data", "Nepal_crop_recommendation_zoned.csv"))
z = z[z["label"].isin(NEPAL_15)][FEATURE_COLS + ["label"]]
df = pd.concat([k, z], ignore_index=True)

X = df[FEATURE_COLS]
y = df["label"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

models = {
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
    "Decision Tree": DecisionTreeClassifier(random_state=42, max_depth=10),
    "SVM (RBF)": Pipeline([("sc", StandardScaler()),
                           ("clf", SVC(kernel="rbf", random_state=42))]),
    "K-Nearest Neighbors": Pipeline([("sc", StandardScaler()),
                                     ("clf", KNeighborsClassifier(n_neighbors=5))]),
    "Logistic Regression": Pipeline([("sc", StandardScaler()),
                                     ("clf", LogisticRegression(max_iter=1000,
                                                                random_state=42))]),
}

print(f"Dataset: {len(df)} rows, {df['label'].nunique()} crops\n")
print(f"{'Algorithm':<22}{'Test Accuracy':>15}")
print("-" * 37)
results = []
for name, model in models.items():
    model.fit(X_train, y_train)
    acc = accuracy_score(y_test, model.predict(X_test))
    results.append((name, acc))
    print(f"{name:<22}{acc:>14.4f}")

print("-" * 37)
best = max(results, key=lambda r: r[1])
print(f"BEST: {best[0]} -> {best[1]:.4f}")
