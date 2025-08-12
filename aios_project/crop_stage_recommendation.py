# import pandas as pd
# import numpy as np
# from sklearn.model_selection import train_test_split
# from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
# from sklearn.linear_model import LinearRegression
# from sklearn.metrics import mean_squared_error, accuracy_score
# from sklearn.preprocessing import LabelEncoder
# import joblib
# import os

# # Load dataset
# data = pd.read_csv("crops_stage.csv")

# # Preprocess the data
# # Example: Parsing fertilizer quantity and application details into separate columns
# data['Fertilizer_Quantity'] = data['Fertilizer Quantity (kg/ha)']  # Assuming this column exists
# data['Application_Timing'] = data['Application Timing']  # Categorical feature for timing
# data['Application_Method'] = data['Application Method']  # Categorical feature for method

# # Encode categorical variables
# label_encoders = {}
# categorical_columns = ['Crop Type', 'Soil Type', 'Fertilizer Recommendations', 'Application Timing', 'Application Method', 'Growth Stages']
# for col in categorical_columns:
#     le = LabelEncoder()
#     data[f'{col}_encoded'] = le.fit_transform(data[col].astype(str))
#     label_encoders[col] = le

# # Parse Fertilizer Quantity to numeric (average if multiple)
# def parse_fert_qty(q):
#     try:
#         return np.mean([float(x.split()[0]) for x in str(q).split(',') if x.strip() and x.split()[0].replace('.', '', 1).isdigit()])
#     except:
#         return 0

# data['Fert_Quantity_num'] = data['Fertilizer Quantity (kg/ha)'].apply(parse_fert_qty)

# # Parse Planting Density to numeric
# data['Planting_Density_num'] = pd.to_numeric(data['Planting Density (plants/ha)'], errors='coerce')

# # Parse Soil pH to numeric (average if range)
# def parse_ph(ph):
#     if isinstance(ph, str) and '–' in ph:
#         parts = ph.replace(' ', '').split('–')
#         try:
#             return (float(parts[0]) + float(parts[1])) / 2
#         except:
#             return np.nan
#     try:
#         return float(ph)
#     except:
#         return np.nan

# data['Soil_pH_num'] = data['Soil pH'].apply(parse_ph)

# # Parse yield range to average and create 'Yield' column
# def parse_yield(y):
#     if isinstance(y, str) and '–' in y:
#         parts = y.replace(' ', '').split('–')
#         try:
#             return (float(parts[0]) + float(parts[1])) / 2
#         except:
#             return np.nan
#     try:
#         return float(y)
#     except:
#         return np.nan

# data['Yield'] = data['Yield Expectation (tons/ha)'].apply(parse_yield)

# # Features and target
# target = 'Yield'
# features = [
#     'Crop Type_encoded', 'Soil_pH_num', 'Soil Type_encoded',
#     'Fertilizer Recommendations_encoded', 'Fert_Quantity_num',
#     'Application Timing_encoded', 'Application Method_encoded',
#     'Planting_Density_num', 'Growth Stages_encoded'
# ]

# X = data[features]
# y = data[target]

# # Drop rows with missing values
# X = X.dropna()
# y = y.loc[X.index]

# # After dropping missing values from X and aligning indices
# y_fertilizer_quantity = data.loc[X.index, 'Fert_Quantity_num']
# y_application_timing = data.loc[X.index, 'Application Timing_encoded']
# y_application_method = data.loc[X.index, 'Application Method_encoded']

# # Train/test split
# X_train, X_test, y_train_fertilizer, y_test_fertilizer = train_test_split(X, y_fertilizer_quantity, test_size=0.2, random_state=42)
# _, _, y_train_timing, y_test_timing = train_test_split(X, y_application_timing, test_size=0.2, random_state=42)
# _, _, y_train_method, y_test_method = train_test_split(X, y_application_method, test_size=0.2, random_state=42)

# # Train models

# # 1. Fertilizer Quantity Model (Regression)
# fertilizer_model = RandomForestRegressor(n_estimators=100, random_state=42)
# fertilizer_model.fit(X_train, y_train_fertilizer)
# y_pred_fertilizer = fertilizer_model.predict(X_test)
# print(f"Fertilizer Quantity Model - MSE: {mean_squared_error(y_test_fertilizer, y_pred_fertilizer)}")

# # 2. Application Timing Model (Classification)
# timing_model = RandomForestClassifier(n_estimators=100, random_state=42)
# timing_model.fit(X_train, y_train_timing)
# y_pred_timing = timing_model.predict(X_test)
# print(f"Application Timing Model - Accuracy: {accuracy_score(y_test_timing, y_pred_timing)}")

# # 3. Application Method Model (Classification)
# method_model = RandomForestClassifier(n_estimators=100, random_state=42)
# method_model.fit(X_train, y_train_method)
# y_pred_method = method_model.predict(X_test)
# print(f"Application Method Model - Accuracy: {accuracy_score(y_test_method, y_pred_method)}")

# # Save models
# joblib.dump(fertilizer_model, 'fertilizer_quantity_model.pkl')
# joblib.dump(timing_model, 'application_timing_model.pkl')
# joblib.dump(method_model, 'application_method_model.pkl')

# print("Models saved as 'fertilizer_quantity_model.pkl', 'application_timing_model.pkl', and 'application_method_model.pkl'.")

# # Save label encoders for all categorical columns in aios_app/ml_models/
# MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'aios_app', 'ml_models')
# os.makedirs(MODEL_DIR, exist_ok=True)
# for col, le in label_encoders.items():
#     joblib.dump(le, os.path.join(MODEL_DIR, f'{col}_label_encoder.pkl'))
#     print(f"Label encoder for '{col}' saved as '{col}_label_encoder.pkl' in {MODEL_DIR}.")

# # Save fertilizer quantity model in aios_app/ml_models/
# joblib.dump(fertilizer_model, os.path.join(MODEL_DIR, 'fertilizer_quantity_model.pkl'))
# print(f"Fertilizer quantity model saved as 'fertilizer_quantity_model.pkl' in {MODEL_DIR}.")

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder
import joblib
import os

# Load dataset
data = pd.read_csv("crops_stage.csv")

print("Dataset shape:", data.shape)
print("Columns:", data.columns.tolist())

# Parse Soil pH to numeric (average if range)
def parse_ph(ph):
    if isinstance(ph, str) and '–' in ph:
        parts = ph.replace(' ', '').split('–')
        try:
            return (float(parts[0]) + float(parts[1])) / 2
        except:
            return np.nan
    try:
        return float(ph)
    except:
        return np.nan

data['Soil_pH_num'] = data['Soil pH'].apply(parse_ph)

# Parse Planting Density to numeric
data['Planting_Density_num'] = pd.to_numeric(data['Planting Density (plants/ha)'], errors='coerce')

# Parse yield range to average
def parse_yield(y):
    if isinstance(y, str) and '–' in y:
        parts = y.replace(' ', '').split('–')
        try:
            return (float(parts[0]) + float(parts[1])) / 2
        except:
            return np.nan
    try:
        return float(y)
    except:
        return np.nan

data['Yield'] = data['Yield Expectation (tons/ha)'].apply(parse_yield)

# Encode categorical variables (INPUT FEATURES ONLY)
label_encoders = {}
input_categorical_columns = ['Crop Type', 'Soil Type', 'Growth Stages']

for col in input_categorical_columns:
    le = LabelEncoder()
    data[f'{col}_encoded'] = le.fit_transform(data[col].astype(str))
    label_encoders[col] = le

# Encode OUTPUT variables separately
output_encoders = {}
output_categorical_columns = ['Fertilizer Recommendations', 'Application Timing', 'Application Method']

for col in output_categorical_columns:
    le = LabelEncoder()
    data[f'{col}_encoded'] = le.fit_transform(data[col].astype(str))
    output_encoders[col] = le

# Parse fertilizer quantity more intelligently
def parse_fert_qty_smart(fert_rec, qty_str):
    """
    Parse fertilizer quantity based on the specific fertilizer recommendation
    """
    try:
        # For complex fertilizer recommendations, extract the main quantity
        if 'Basal' in str(fert_rec):
            # Extract basal application amount
            if 'kg/ha' in str(qty_str):
                numbers = [float(x) for x in str(qty_str).replace(',', ' ').split() if x.replace('.', '').isdigit()]
                return numbers[0] if numbers else 0
        return np.mean([float(x.split()[0]) for x in str(qty_str).split(',') if x.strip() and x.split()[0].replace('.', '', 1).isdigit()])
    except:
        return 0

data['Fert_Quantity_num'] = data.apply(
    lambda row: parse_fert_qty_smart(row['Fertilizer Recommendations'], row['Fertilizer Quantity (kg/ha)']), 
    axis=1
)

# Define features (NO TARGET LEAKAGE)
features = [
    'Crop Type_encoded', 
    'Soil_pH_num', 
    'Soil Type_encoded',
    'Planting_Density_num', 
    'Growth Stages_encoded'
]

# Clean data
X = data[features].dropna()
valid_indices = X.index

# Define multiple targets
y_fertilizer_rec = data.loc[valid_indices, 'Fertilizer Recommendations_encoded']
y_fertilizer_qty = data.loc[valid_indices, 'Fert_Quantity_num']
y_application_timing = data.loc[valid_indices, 'Application Timing_encoded']
y_application_method = data.loc[valid_indices, 'Application Method_encoded']
y_yield = data.loc[valid_indices, 'Yield']

print(f"Training data shape: {X.shape}")
print(f"Features: {features}")

# Train/test split
X_train, X_test, y_fert_rec_train, y_fert_rec_test = train_test_split(
    X, y_fertilizer_rec, test_size=0.2, random_state=42, stratify=y_fertilizer_rec
)

# Get corresponding splits for other targets
_, _, y_fert_qty_train, y_fert_qty_test = train_test_split(
    X, y_fertilizer_qty, test_size=0.2, random_state=42
)
_, _, y_timing_train, y_timing_test = train_test_split(
    X, y_application_timing, test_size=0.2, random_state=42
)
_, _, y_method_train, y_method_test = train_test_split(
    X, y_application_method, test_size=0.2, random_state=42
)
_, _, y_yield_train, y_yield_test = train_test_split(
    X, y_yield, test_size=0.2, random_state=42
)

# Train Models
models = {}

# 1. Fertilizer Recommendation Model (Classification)
fert_rec_model = RandomForestClassifier(n_estimators=100, random_state=42)
fert_rec_model.fit(X_train, y_fert_rec_train)
y_pred_fert_rec = fert_rec_model.predict(X_test)
models['fertilizer_recommendation'] = fert_rec_model

print(f"Fertilizer Recommendation Model - Accuracy: {accuracy_score(y_fert_rec_test, y_pred_fert_rec):.3f}")

# 2. Fertilizer Quantity Model (Regression)
fert_qty_model = RandomForestRegressor(n_estimators=100, random_state=42)
fert_qty_model.fit(X_train, y_fert_qty_train)
y_pred_fert_qty = fert_qty_model.predict(X_test)
models['fertilizer_quantity'] = fert_qty_model

print(f"Fertilizer Quantity Model - MSE: {mean_squared_error(y_fert_qty_test, y_pred_fert_qty):.3f}")

# 3. Application Timing Model (Classification)
timing_model = RandomForestClassifier(n_estimators=100, random_state=42)
timing_model.fit(X_train, y_timing_train)
y_pred_timing = timing_model.predict(X_test)
models['application_timing'] = timing_model

print(f"Application Timing Model - Accuracy: {accuracy_score(y_timing_test, y_pred_timing):.3f}")

# 4. Application Method Model (Classification)
method_model = RandomForestClassifier(n_estimators=100, random_state=42)
method_model.fit(X_train, y_method_train)
y_pred_method = method_model.predict(X_test)
models['application_method'] = method_model

print(f"Application Method Model - Accuracy: {accuracy_score(y_method_test, y_pred_method):.3f}")

# 5. Yield Prediction Model (Regression)
yield_model = RandomForestRegressor(n_estimators=100, random_state=42)
yield_model.fit(X_train, y_yield_train)
y_pred_yield = yield_model.predict(X_test)
models['yield_prediction'] = yield_model

print(f"Yield Prediction Model - MSE: {mean_squared_error(y_yield_test, y_pred_yield):.3f}")

# Create model directory
MODEL_DIR = 'ml_models'
os.makedirs(MODEL_DIR, exist_ok=True)

# Save all models
for model_name, model in models.items():
    joblib.dump(model, os.path.join(MODEL_DIR, f'{model_name}_model.pkl'))
    print(f"Saved {model_name} model")

# Save encoders
for col, le in label_encoders.items():
    joblib.dump(le, os.path.join(MODEL_DIR, f'{col}_label_encoder.pkl'))

for col, le in output_encoders.items():
    joblib.dump(le, os.path.join(MODEL_DIR, f'{col}_output_encoder.pkl'))

print("All models and encoders saved successfully!")

# Test prediction function
def predict_crop_recommendations(crop_type, soil_ph, soil_type, planting_density, growth_stage):
    """
    Make predictions for a given crop and conditions
    """
    # Encode inputs
    crop_encoded = label_encoders['Crop Type'].transform([crop_type])[0]
    soil_type_encoded = label_encoders['Soil Type'].transform([soil_type])[0]
    growth_stage_encoded = label_encoders['Growth Stages'].transform([growth_stage])[0]
    
    # Create feature vector
    features_vector = np.array([[crop_encoded, soil_ph, soil_type_encoded, planting_density, growth_stage_encoded]])
    
    # Make predictions
    fert_rec_pred = models['fertilizer_recommendation'].predict(features_vector)[0]
    fert_qty_pred = models['fertilizer_quantity'].predict(features_vector)[0]
    timing_pred = models['application_timing'].predict(features_vector)[0]
    method_pred = models['application_method'].predict(features_vector)[0]
    yield_pred = models['yield_prediction'].predict(features_vector)[0]
    
    # Decode predictions
    fert_rec_decoded = output_encoders['Fertilizer Recommendations'].inverse_transform([fert_rec_pred])[0]
    timing_decoded = output_encoders['Application Timing'].inverse_transform([timing_pred])[0]
    method_decoded = output_encoders['Application Method'].inverse_transform([method_pred])[0]
    
    return {
        'fertilizer_recommendation': fert_rec_decoded,
        'fertilizer_quantity': fert_qty_pred,
        'application_timing': timing_decoded,
        'application_method': method_decoded,
        'predicted_yield': yield_pred
    }

# Test with Maize example
test_prediction = predict_crop_recommendations(
    crop_type='Maize',
    soil_ph=6.0,
    soil_type='Loamy',
    planting_density=66667,
    growth_stage='Vegetative'
)

print("\nTest Prediction for Maize:")
for key, value in test_prediction.items():
    print(f"{key}: {value}")
