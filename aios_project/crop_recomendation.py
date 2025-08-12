# import pandas as pd
# import numpy as np
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import LabelEncoder
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.linear_model import LogisticRegression
# from sklearn.svm import SVC
# from xgboost import XGBClassifier
# from sklearn.metrics import accuracy_score, classification_report
# from pathlib import Path

# # Load the dataset
# current_dir = Path(__file__).parent  # aios_project directory
# data_path = current_dir.parent / 'Crop_Recommendation.csv'  # backend/Crop_Recommendation.csv
# data = pd.read_csv(data_path)

# # Display basic info and first few rows
# print("=== Dataset Overview ===")
# print(f"Dataset shape: {data.shape}")
# print(f"Columns: {data.columns.tolist()}")
# print("\nFirst 5 rows:")
# print(data.head())

# # Preprocess the data (handle categorical variables)
# label_encoders = {}

# # Encode categorical columns using LabelEncoder
# categorical_columns = ['Crop']  # Only 'Crop' is categorical in this dataset
# for col in categorical_columns:
#     le = LabelEncoder()
#     data[f'{col}_encoded'] = le.fit_transform(data[col])
#     label_encoders[col] = le

# # Feature matrix (X) and target vector (y)
# # Using all available features except the target variable
# X = data[['Nitrogen', 'Phosphorus', 'Potassium', 'Temperature', 'Humidity', 'pH', 'Rainfall']]
# y = data['Crop_encoded']

# print(f"\nFeature columns: {X.columns.tolist()}")
# print(f"Number of features: {X.shape[1]}")
# print(f"Number of samples: {X.shape[0]}")

# # Split data into training and testing sets
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# # Initialize models
# models = {
#     'Random Forest': RandomForestClassifier(random_state=42, n_estimators=100),
#     'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
#     'SVM': SVC(random_state=42, probability=True),
#     'XGBoost': XGBClassifier(random_state=42, eval_metric='logloss')
# }

# # Train and evaluate models
# print("\n" + "="*50)
# print("MODEL TRAINING AND EVALUATION")
# print("="*50)

# for model_name, model in models.items():
#     print(f"\nTraining {model_name}...")
#     model.fit(X_train, y_train)
    
#     # Make predictions
#     y_pred = model.predict(X_test)
    
#     # Calculate accuracy and generate classification report
#     accuracy = accuracy_score(y_test, y_pred)
#     print(f"{model_name} Accuracy: {accuracy * 100:.2f}%")
    
#     # Classification report
#     print(f"{model_name} Classification Report:")
#     print(classification_report(y_test, y_pred))

# # Save the best model (Random Forest typically performs well)
# best_model = models['Random Forest']
# print(f"\nBest model (Random Forest) saved for predictions.")
# print(f"Available crops: {label_encoders['Crop'].classes_}")

# import joblib

# # Save the best model (Random Forest) using joblib
# joblib.dump(best_model, 'random_forest_model.pkl')
# print(f"Best model (Random Forest) saved as 'random_forest_model.pkl'.")

# # Save the label encoders for each categorical column
# for col, le in label_encoders.items():
#     joblib.dump(le, f'{col}_label_encoder.pkl')
#     print(f"Label encoder for '{col}' saved as '{col}_label_encoder.pkl'.")

# # Save the feature names as JSON
# import json
# import os
# MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ml_models')
# os.makedirs(MODEL_DIR, exist_ok=True)
# crop_feature_names = list(X.columns)
# with open(os.path.join(MODEL_DIR, 'crop_feature_names.json'), 'w') as f:
#     json.dump(crop_feature_names, f)
# print(f"Crop feature names saved as 'crop_feature_names.json' in {MODEL_DIR}.")

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report
from pathlib import Path
import joblib  # Import joblib for saving the model

# Load the dataset
current_dir = Path(__file__).parent  # aios_project directory
data_path = current_dir.parent / 'Crop_Recommendation.csv'  # Replace with correct path to your dataset
data = pd.read_csv(data_path)

# Display basic info and first few rows
print("=== Dataset Overview ===")
print(f"Dataset shape: {data.shape}")
print(f"Columns: {data.columns.tolist()}")
print("\nFirst 5 rows:")
print(data.head())

# Preprocess the data (handle categorical variables)
label_encoders = {}

# Encode categorical columns using LabelEncoder
categorical_columns = ['Crop']  # Only 'Crop' is categorical in this dataset
for col in categorical_columns:
    le = LabelEncoder()
    data[f'{col}_encoded'] = le.fit_transform(data[col])
    label_encoders[col] = le

# Feature matrix (X) and target vector (y)
# Using all available features except the target variable
X = data[['Nitrogen', 'Phosphorus', 'Potassium', 'Temperature', 'Humidity', 'pH', 'Rainfall']]
y = data['Crop_encoded']  # Target variable for crop prediction

print(f"\nFeature columns: {X.columns.tolist()}")
print(f"Number of features: {X.shape[1]}")
print(f"Number of samples: {X.shape[0]}")

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize models for Crop prediction
models = {
    'Random Forest': RandomForestClassifier(random_state=42, n_estimators=100),
    'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
    'SVM': SVC(random_state=42, probability=True),
    'XGBoost': XGBClassifier(random_state=42, eval_metric='logloss')
}

# Train and evaluate models for Crop prediction
print("\n" + "="*50)
print("MODEL TRAINING AND EVALUATION")
print("="*50)

for model_name, model in models.items():
    print(f"\nTraining {model_name} for Crop Prediction...")
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate accuracy and generate classification report
    accuracy = accuracy_score(y_test, y_pred)
    print(f"{model_name} Accuracy: {accuracy * 100:.2f}%")
    
    # Classification report
    print(f"{model_name} Classification Report:")
    print(classification_report(y_test, y_pred))

# Save the best model (Random Forest typically performs well)
best_model = models['Random Forest']
print(f"\nBest model (Random Forest) saved for predictions.")
print(f"Available crops: {label_encoders['Crop'].classes_}")

# Save the best model using joblib with a new name for the crop model
joblib.dump(best_model, 'crop_model.pkl')
print(f"Best crop model (Random Forest) saved as 'crop_model.pkl'.")

# Save the label encoder for 'Crop' using joblib
for col, le in label_encoders.items():
    joblib.dump(le, f'{col}_label_encoder.pkl')
    print(f"Label encoder for '{col}' saved as '{col}_label_encoder.pkl'.")

