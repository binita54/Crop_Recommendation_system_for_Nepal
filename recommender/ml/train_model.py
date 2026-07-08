import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

def create_global_crop_dataset():
    crops_data = [
        {'N': 90, 'P': 40, 'K': 40, 'temperature': 25, 'humidity': 80, 'ph': 7, 'rainfall': 200, 'label': 'rice'},
        {'N': 80, 'P': 35, 'K': 45, 'temperature': 22, 'humidity': 70, 'ph': 6.5, 'rainfall': 150, 'label': 'maize'},
        {'N': 60, 'P': 50, 'K': 200, 'temperature': 20, 'humidity': 65, 'ph': 6.8, 'rainfall': 100, 'label': 'wheat'},
        {'N': 40, 'P': 30, 'K': 250, 'temperature': 18, 'humidity': 60, 'ph': 7.2, 'rainfall': 80, 'label': 'chickpea'},
        {'N': 50, 'P': 45, 'K': 220, 'temperature': 16, 'humidity': 55, 'ph': 7.0, 'rainfall': 90, 'label': 'lentil'},
        {'N': 85, 'P': 35, 'K': 300, 'temperature': 28, 'humidity': 75, 'ph': 6.5, 'rainfall': 200, 'label': 'mango'},
        {'N': 95, 'P': 30, 'K': 350, 'temperature': 26, 'humidity': 85, 'ph': 6.2, 'rainfall': 250, 'label': 'banana'},
        {'N': 70, 'P': 45, 'K': 280, 'temperature': 24, 'humidity': 70, 'ph': 6.8, 'rainfall': 180, 'label': 'orange'},
        {'N': 65, 'P': 55, 'K': 400, 'temperature': 15, 'humidity': 80, 'ph': 6.0, 'rainfall': 800, 'label': 'apple'},
        {'N': 45, 'P': 50, 'K': 380, 'temperature': 28, 'humidity': 65, 'ph': 7.0, 'rainfall': 60, 'label': 'coffee'},
        {'N': 75, 'P': 30, 'K': 320, 'temperature': 30, 'humidity': 50, 'ph': 6.5, 'rainfall': 50, 'label': 'watermelon'},
        {'N': 55, 'P': 40, 'K': 200, 'temperature': 26, 'humidity': 55, 'ph': 7.5, 'rainfall': 60, 'label': 'muskmelon'},
        {'N': 85, 'P': 25, 'K': 300, 'temperature': 24, 'humidity': 75, 'ph': 6.8, 'rainfall': 200, 'label': 'grapes'},
        {'N': 88, 'P': 45, 'K': 330, 'temperature': 22, 'humidity': 80, 'ph': 7.2, 'rainfall': 500, 'label': 'coconut'},
        {'N': 40, 'P': 45, 'K': 180, 'temperature': 20, 'humidity': 60, 'ph': 6.5, 'rainfall': 1000, 'label': 'jute'},
        {'N': 75, 'P': 35, 'K': 280, 'temperature': 25, 'humidity': 55, 'ph': 6.8, 'rainfall': 400, 'label': 'cotton'},
        {'N': 60, 'P': 35, 'K': 150, 'temperature': 30, 'humidity': 40, 'ph': 7.0, 'rainfall': 350, 'label': 'mothbeans'},
        {'N': 70, 'P': 40, 'K': 200, 'temperature': 28, 'humidity': 65, 'ph': 7.0, 'rainfall': 380, 'label': 'pigeonpeas'},
    ]
    
    # Duplicate and vary for more training samples
    for crop in crops_data.copy():
        for delta in [(5,5,5,2,5,0.2,20), (-5,-5,-5,-2,-5,-0.2,-20)]:
            new_crop = {
                'N': max(10, crop['N'] + delta[0]),
                'P': max(10, crop['P'] + delta[1]),
                'K': max(50, crop['K'] + delta[2]),
                'temperature': max(5, crop['temperature'] + delta[3]),
                'humidity': max(10, crop['humidity'] + delta[4]),
                'ph': max(5, min(8, crop['ph'] + delta[5])),
                'rainfall': max(20, crop['rainfall'] + delta[6]),
                'label': crop['label']
            }
            crops_data.append(new_crop)
    
    return pd.DataFrame(crops_data)

def train_and_save_model():
    df = create_global_crop_dataset()
    X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
    y = df['label']
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    pkl_path = os.path.join(os.path.dirname(__file__), 'Crop_recommendation_RF.pkl')
    with open(pkl_path, 'wb') as f:
        pickle.dump({
            'model': model,
            'feature_cols': ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        }, f)
    print(f"Global+Nepal model saved to {pkl_path}")

if __name__ == '__main__':
    train_and_save_model()