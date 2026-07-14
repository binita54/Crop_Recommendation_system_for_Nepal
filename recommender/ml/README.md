# Machine Learning Training Pipeline — `recommender/ml/`

This folder contains the trained models and the scripts that build them for the
**AgroSmart** crop-recommendation and disease-detection system.

---

## 1. Crop Recommendation Model (`Crop_recommendation_RF.pkl`)

**Algorithm:** Random Forest Classifier (scikit-learn, 100 trees).
**Inputs (7 features):** `N, P, K, temperature, humidity, ph, rainfall`
**Output:** one of 15 Nepal crops (banana, barley, blackgram, chickpea, ginger,
lentil, maize, mango, millet, mustard, potato, rice, soybean, sugarcane, wheat).

### Dataset (merged — honest disclosure)
No public dataset is simultaneously *real* and *complete* for Nepal's 15 crops.
We therefore merge two sources:

| Source | Real? | Crops covered | Rows used |
|---|---|---|---|
| Kaggle *Crop Recommendation Dataset* (Atharva Ingle) | **Yes** | 7 overlapping Nepal crops (rice, maize, chickpea, blackgram, lentil, banana, mango) | 700 |
| Synthetic zoned dataset (`build_nepal_zoned_dataset.py`) | No (anchored to NARC/CIMMYT agronomy) | 8 Nepal-only crops (wheat, potato, sugarcane, barley, ginger, millet, mustard, soybean) | 1160 |

Result: **1860 rows, 15 Nepal crops, ~93% test accuracy.**

### How to retrain
```bash
# from project root
.\.venv\Scripts\python.exe recommender/ml/train_hybrid_model.py
```
This reads `Crop_recommendation_kaggle.csv` (real) and
`data/Nepal_crop_recommendation_zoned.csv` (synthetic), trains the forest, and
overwrites `Crop_recommendation_RF.pkl`.

### Files
- `train_hybrid_model.py` — **OFFICIAL** crop-training script (use this).
- `Crop_recommendation_kaggle.csv` — real Kaggle data (2200 rows, 22 crops).
- `build_nepal_zoned_dataset.py` — generates the synthetic zoned CSV.
- `train_zoned_model.py` — legacy script (trains on synthetic data only).
- `train_model.py` — early prototype (29 crops, tiny hand-made data; not used).
- `collect_nepal_data.py` — collects REAL Nepal soil values from the NARC
  Digital Soil Map API (evidence / future live-feature; not used for training
  because NARC's crop labels are location-independent).

### Real Nepal soil data (collected, not yet used for labels)
`collect_nepal_data.py` queries `https://soil.narc.gov.np/soil/api/?lat={lat}&lon={lon}`
(NARC + CIMMYT, Dec 2024) and returns real measured soil N/P/K/pH across Nepal.
Future work: collect real field labels for all 15 crops and retrain end-to-end
on 100% Nepal data.

---

## 2. Disease Detection Model (`multi_crop_disease_model.h5`)

**Algorithm:** Convolutional Neural Network (TensorFlow/Keras).
**Input:** 64×64 RGB leaf image. **Output:** 28 disease classes across 7 crops
(Maize, Potato, Rice, Mango, Sugarcane, Wheat, Banana).

### Dataset (real, 11,526 images, 28 classes)
Trained in Google Colab (`AgroSmart_7Crop_Disease_Training1.ipynb`):
- Maize + Potato — plant64.npz (downsampled plant-disease dataset)
- Rice — RiceDiseases-DataSet (GitHub)
- Mango — Mango-Leaf-Disease-Detection (GitHub)
- Sugarcane — Sugarcane-Leaf-Disease-Detection (GitHub)
- Wheat — Kaggle `olyadgetch/wheat-leaf-dataset`
- Banana — Mendeley `BananaLSD` dataset (9tb7k297ff)
**Test accuracy: 87.25%** on 1,153 held-out images.

### Files
- `multi_crop_disease_model.h5` — trained CNN weights.
- `class_names.txt` — 28 output class names.
- `disease_loader.py` — image preprocessing + inference (`predict_disease`).
- `AgroSmart_7Crop_Disease_Training1.ipynb` — Colab training notebook (keep in repo).

---

## Dataset Citations (IEEE style — for the project report)

[1] A. Ingle, "Crop Recommendation Dataset," Kaggle. [Online]. Available:
    https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset

[2] attaullah, "Downsampled Plant Disease Dataset (plant64.npz)," GitHub.
    [Online]. Available:
    https://github.com/attaullah/downsampled-plant-disease-dataset

[3] aldrin233, "RiceDiseases-DataSet," GitHub. [Online]. Available:
    https://github.com/aldrin233/RiceDiseases-DataSet

[4] Anas436, "Mango-Leaf-Disease-Detection," GitHub. [Online]. Available:
    https://github.com/Anas436/Mango-Leaf-Disease-Detection

[5] RoshitaB, "Sugarcane-Leaf-Disease-Detection," GitHub. [Online]. Available:
    https://github.com/RoshitaB/Sugarcane-Leaf-Disease-Detection

[6] olyadgetch, "Wheat Leaf Dataset," Kaggle. [Online]. Available:
    https://www.kaggle.com/datasets/olyadgetch/wheat-leaf-dataset

[7] P. Gonzalez-De-La-Cruz et al., "Banana Leaf Spot Diseases (BananaLSD)
    Dataset," Mendeley Data, 2022. [Online]. Available:
    https://data.mendeley.com/datasets/9tb7k297ff/1

[8] Nepal Agricultural Research Council (NARC) and CIMMYT, "Digital Soil Map
    of Nepal," 2024. [Online]. Available: https://soil.narc.gov.np/data
