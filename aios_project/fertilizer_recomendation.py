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
# import joblib  # Import joblib for saving the model
# import json
# import os

# # Load the dataset
# current_dir = Path(__file__).parent  # aios_project directory
# data_path = current_dir.parent / 'fertilizer_dataset.csv'  # Replace with correct path to your dataset
# data = pd.read_csv(data_path)

# # Display basic info and first few rows
# print("=== FERTILIZER RECOMMENDATION DATASET OVERVIEW ===")
# print(f"Dataset shape: {data.shape}")
# print(f"Columns: {data.columns.tolist()}")
# print("\nFirst 5 rows:")
# print(data.head())

# # Drop the 'District_Name' and 'Link' columns
# data = data.drop(columns=['District_Name', 'Link'])

# # Preprocess the data (handle categorical variables)
# label_encoders = {}

# # Encode categorical columns using LabelEncoder
# categorical_columns = ['Soil_color', 'Crop', 'Fertilizer']
# for col in categorical_columns:
#     le = LabelEncoder()
#     data[f'{col}_encoded'] = le.fit_transform(data[col])
#     label_encoders[col] = le

# # Feature matrix (X) and target vectors (y) for Crop and Fertilizer predictions
# X = data[['Soil_color_encoded', 'Nitrogen', 'Phosphorus', 'Potassium', 'pH', 'Rainfall', 'Temperature']]
# y_crop = data['Crop_encoded']  # Target variable for crop prediction
# y_fertilizer = data['Fertilizer_encoded']  # Target variable for fertilizer prediction

# print(f"\nFeature columns: {X.columns.tolist()}")
# print(f"Number of features: {X.shape[1]}")
# print(f"Number of samples: {X.shape[0]}")

# # Split data into training and testing sets for both Crop and Fertilizer predictions
# X_train, X_test, y_train_crop, y_test_crop = train_test_split(X, y_crop, test_size=0.2, random_state=42)
# _, _, y_train_fertilizer, y_test_fertilizer = train_test_split(X, y_fertilizer, test_size=0.2, random_state=42)

# # Initialize models
# models = {
#     'Random Forest': RandomForestClassifier(random_state=42, n_estimators=100),
#     'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
#     'SVM': SVC(random_state=42, probability=True),
#     'XGBoost': XGBClassifier(random_state=42, eval_metric='logloss')
# }

# # Train and evaluate models for Crop prediction
# print("\n" + "="*50)
# print("MODEL TRAINING AND EVALUATION - CROP PREDICTION")
# print("="*50)

# for model_name, model in models.items():
#     print(f"\nTraining {model_name} for Crop Prediction...")
#     model.fit(X_train, y_train_crop)
    
#     # Make predictions
#     y_pred_crop = model.predict(X_test)
    
#     # Calculate accuracy and generate classification report
#     accuracy_crop = accuracy_score(y_test_crop, y_pred_crop)
#     print(f"{model_name} Accuracy for Crop Prediction: {accuracy_crop * 100:.2f}%")
#     print(f"{model_name} Classification Report for Crop Prediction:")
#     print(classification_report(y_test_crop, y_pred_crop))

# # Train and evaluate models for Fertilizer prediction
# print("\n" + "="*50)
# print("MODEL TRAINING AND EVALUATION - FERTILIZER PREDICTION")
# print("="*50)

# for model_name, model in models.items():
#     print(f"\nTraining {model_name} for Fertilizer Prediction...")
#     model.fit(X_train, y_train_fertilizer)
    
#     # Make predictions
#     y_pred_fertilizer = model.predict(X_test)
    
#     # Calculate accuracy and generate classification report
#     accuracy_fertilizer = accuracy_score(y_test_fertilizer, y_pred_fertilizer)
#     print(f"{model_name} Accuracy for Fertilizer Prediction: {accuracy_fertilizer * 100:.2f}%")
#     print(f"{model_name} Classification Report for Fertilizer Prediction:")
#     print(classification_report(y_test_fertilizer, y_pred_fertilizer))

# # Save the best models (Random Forest typically performs well)
# best_model_crop = models['Random Forest']
# best_model_fertilizer = models['Random Forest']
# print(f"\nBest model for Crop Prediction (Random Forest) saved.")
# print(f"Best model for Fertilizer Prediction (Random Forest) saved.")

# # Save the models using joblib
# joblib.dump(best_model_crop, 'best_model_crop.pkl')
# joblib.dump(best_model_fertilizer, 'best_model_fertilizer.pkl')

# # Save the label encoders using joblib
# for col, le in label_encoders.items():
#     joblib.dump(le, f'{col}_label_encoder.pkl')
#     print(f"Label encoder for '{col}' saved as '{col}_label_encoder.pkl'.")

# # Save the feature names as JSON
# MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ml_models')
# os.makedirs(MODEL_DIR, exist_ok=True)
# fertilizer_feature_names = list(X.columns)
# with open(os.path.join(MODEL_DIR, 'fertilizer_feature_names.json'), 'w') as f:
#     json.dump(fertilizer_feature_names, f)
# print(f"Fertilizer feature names saved as 'fertilizer_feature_names.json' in {MODEL_DIR}.")
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
import json
import os

# Load the dataset
current_dir = Path(__file__).parent  # aios_project directory
data_path = current_dir.parent / 'fertilizer_dataset.csv'  # Replace with correct path to your dataset
data = pd.read_csv(data_path)

# Display basic info and first few rows
print("=== FERTILIZER RECOMMENDATION DATASET OVERVIEW ===")
print(f"Dataset shape: {data.shape}")
print(f"Columns: {data.columns.tolist()}")
print("\nFirst 5 rows:")
print(data.head())

# Drop the 'District_Name' and 'Link' columns as they are unnecessary
data = data.drop(columns=['District_Name', 'Link'])

# Encode categorical columns using LabelEncoder
label_encoders = {}

# Encode 'Soil_color', 'Crop', and 'Fertilizer' columns directly
categorical_columns = ['Soil_color', 'Crop', 'Fertilizer']
for col in categorical_columns:
    le = LabelEncoder()
    data[f'{col}_encoded'] = le.fit_transform(data[col])
    label_encoders[col] = le

# Feature matrix (X) and target vector (y) for Fertilizer prediction
X = data[['Soil_color_encoded', 'Nitrogen', 'Phosphorus', 'Potassium', 'pH', 'Rainfall', 'Temperature']]  # Use encoded 'Soil_color'
y_fertilizer = data['Fertilizer']  # Target variable for fertilizer prediction (actual fertilizer names)

# Encode the target variable (Fertilizer) using LabelEncoder to convert to numeric
fertilizer_label_encoder = label_encoders['Fertilizer']  # Save the encoder for 'Fertilizer'
y_fertilizer_encoded = fertilizer_label_encoder.transform(y_fertilizer)

# Split data into training and testing sets for fertilizer prediction
X_train, X_test, y_train_fertilizer, y_test_fertilizer = train_test_split(X, y_fertilizer_encoded, test_size=0.2, random_state=42)

# Initialize models for Fertilizer prediction
models = {
    'Random Forest': RandomForestClassifier(random_state=42, n_estimators=100),
    'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
    'SVM': SVC(random_state=42, probability=True),
    'XGBoost': XGBClassifier(random_state=42, eval_metric='logloss')
}

# Train and evaluate models for Fertilizer prediction
print("\n" + "="*50)
print("MODEL TRAINING AND EVALUATION - FERTILIZER PREDICTION")
print("="*50)

for model_name, model in models.items():
    print(f"\nTraining {model_name} for Fertilizer Prediction...")
    model.fit(X_train, y_train_fertilizer)
    
    # Make predictions
    y_pred_fertilizer = model.predict(X_test)
    
    # Calculate accuracy and generate classification report
    accuracy_fertilizer = accuracy_score(y_test_fertilizer, y_pred_fertilizer)
    print(f"{model_name} Accuracy for Fertilizer Prediction: {accuracy_fertilizer * 100:.2f}%")
    print(f"{model_name} Classification Report for Fertilizer Prediction:")
    print(classification_report(y_test_fertilizer, y_pred_fertilizer))

# Save the best model (Random Forest typically performs well)
best_model_fertilizer = models['Random Forest']
print(f"\nBest model for Fertilizer Prediction (Random Forest) saved.")

# Save the fertilizer model using joblib
joblib.dump(best_model_fertilizer, 'best_model_fertilizer.pkl')
print(f"Best fertilizer model (Random Forest) saved as 'best_model_fertilizer.pkl'.")

# Save the fertilizer label encoder using joblib
joblib.dump(fertilizer_label_encoder, 'fertilizer_label_encoder.pkl')
print(f"Label encoder for 'Fertilizer' saved as 'fertilizer_label_encoder.pkl'.")
