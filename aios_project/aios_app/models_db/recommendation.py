
# from django.db import models
# from .user import User
# import joblib
# import numpy as np
# import os
# import pandas as pd
# import json

# class CropRecommendation(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
#     temperature = models.FloatField()
#     humidity = models.FloatField()
#     moisture = models.FloatField()
#     soil_type = models.CharField(max_length=50)  # (e.g., Sandy, Loamy, Black, etc.)
#     nitrogen = models.IntegerField()
#     potassium = models.IntegerField()
#     phosphorous = models.IntegerField()
#     crop_predicted = models.CharField(max_length=50)  # The predicted crop type
#     fertilizer_predicted = models.CharField(max_length=50)  # The predicted fertilizer
#     timestamp = models.DateTimeField(auto_now_add=True)  # Timestamp of when the recommendation was made
#     status = models.CharField(max_length=50, default='Pending')  # Pending, Confirmed, etc.

#     def __str__(self):
#         return f"{self.user.username if self.user else 'Anonymous'} - {self.crop_predicted} - {self.fertilizer_predicted}"

#     class Meta:
#         verbose_name = 'Crop Recommendation'
#         verbose_name_plural = 'Crop Recommendations'

#     @staticmethod
#     def predict_and_save_recommendation(user, input_data):
#         """
#         Predict crop and fertilizer recommendations based on the input data and save them to the database.
#         :param user: The user requesting the recommendation (instance of User model).
#         :param input_data: Input data as a dict with all possible features.
#         :return: The created CropRecommendation object.
#         """
#         BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#         MODEL_DIR = os.path.join(BASE_DIR, 'ml_models')
        
#         try:
#             # Load models and label encoders
#             crop_model = joblib.load(os.path.join(MODEL_DIR, 'crop_model.pkl'))
#             fertilizer_model = joblib.load(os.path.join(MODEL_DIR, 'best_model_fertilizer.pkl'))
#             crop_encoder = joblib.load(os.path.join(MODEL_DIR, 'Crop_label_encoder.pkl'))
#             fertilizer_encoder = joblib.load(os.path.join(MODEL_DIR, 'Fertilizer_label_encoder.pkl'))
#         except Exception as e:
#             print(f"Error loading models or label encoders: {e}")
#             return None

#         # Hardcoded feature names (must match training)
#         crop_feature_names = ['Nitrogen', 'Phosphorus', 'Potassium', 'Temperature', 'Humidity', 'pH', 'Rainfall']
#         fertilizer_feature_names = ['Soil_color_encoded', 'Nitrogen', 'Phosphorus', 'Potassium', 'pH', 'Rainfall', 'Temperature']

#         # Prepare input dict with defaults
#         input_dict = {k: input_data.get(k, 0) for k in set(crop_feature_names + fertilizer_feature_names)}

#         # Ensure correct encoding for Soil_type using Fertilizer encoder
#         if 'Soil_color_encoded' in input_dict and fertilizer_encoder is not None:
#             try:
#                 input_dict['Soil_color_encoded'] = fertilizer_encoder.transform([input_dict['Soil_color_encoded']])[0]
#             except Exception:
#                 input_dict['Soil_color_encoded'] = 0

#         # Make sure the columns match what the model expects
#         # DataFrame for crop model
#         crop_df = pd.DataFrame([{k: input_dict.get(k, 0) for k in crop_feature_names}])
#         # DataFrame for fertilizer model
#         fertilizer_df = pd.DataFrame([{k: input_dict.get(k, 0) for k in fertilizer_feature_names}])

#         # Predict crop
#         crop_prediction = crop_model.predict(crop_df)[0]
#         crop_predicted = crop_encoder.inverse_transform([crop_prediction])[0]

#         # Predict fertilizer
#         fertilizer_prediction = fertilizer_model.predict(fertilizer_df)[0]
#         fertilizer_predicted = fertilizer_encoder.inverse_transform([fertilizer_prediction])[0]

#         # Decode soil type for storage
#         try:
#             soil_type_decoded = fertilizer_encoder.inverse_transform([int(input_dict['Soil_color'])])[0]
#         except Exception:
#             soil_type_decoded = 'Unknown'

#         # Safety for phosphorous
#         phosphorous = input_dict.get('Phosphorus', 0)

#         # Create and save recommendation
#         recommendation = CropRecommendation.objects.create(
#             user=user,
#             temperature=input_dict.get('Temperature', 0),
#             humidity=input_dict.get('Humidity', 0),
#             moisture=input_dict.get('Moisture', 0),
#             soil_type=soil_type_decoded,  # Decode to actual soil type
#             nitrogen=input_dict.get('Nitrogen', 0),
#             potassium=input_dict.get('Potassium', 0),
#             phosphorous=phosphorous,
#             crop_predicted=crop_predicted,
#             fertilizer_predicted=fertilizer_predicted,
#             status='Pending'
#         )
#         return recommendation

#    


# models_db/recommendation.py
from django.db import models
from .user import User
import joblib, os, pandas as pd

class CropRecommendation(models.Model):
    STATUS_CHOICES = [
        ('pending_review', 'Pending Review'),
        ('in_review', 'In Review'),
        ('translated', 'Translated'),
        ('returned', 'Returned to Farmer'),
    ]

    # Who requested (farmer)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='crop_recommendations')

    # Who reviews (agronomist)
    agronomist = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='crop_reviews')

    # Original numeric fields (kept for compatibility)
    temperature = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    moisture = models.FloatField(null=True, blank=True)
    soil_type = models.CharField(max_length=50, blank=True)  # e.g., Sandy, Loamy
    nitrogen = models.IntegerField(null=True, blank=True)
    potassium = models.IntegerField(null=True, blank=True)
    phosphorous = models.IntegerField(null=True, blank=True)

    crop_predicted = models.CharField(max_length=50, blank=True)
    fertilizer_predicted = models.CharField(max_length=50, blank=True)

    # New: full payloads for traceability
    farmer_inputs = models.JSONField(default=dict, blank=True)     # raw formData
    ai_outputs = models.JSONField(default=dict, blank=True)        # full/crop-only results
    fertilizer_plan = models.JSONField(default=dict, blank=True)   # optional extra

    # Agronomist fields
    agronomist_notes = models.TextField(blank=True)
    translated_summary = models.TextField(blank=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='pending_review')

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        u = self.user.username if self.user else 'Anonymous'
        return f"{u} • {self.crop_predicted or 'N/A'} • {self.fertilizer_predicted or 'N/A'}"

    class Meta:
        verbose_name = 'Crop Recommendation'
        verbose_name_plural = 'Crop Recommendations'
        ordering = ['-timestamp']

    # Static methods should be outside the Meta class
    @staticmethod
    def predict_and_save_crop_only(user, input_data):
        """
        Predict crop recommendation based on the input data and save it to the database, without predicting fertilizer.
        :param user: The user requesting the recommendation (instance of User model).
        :param input_data: Input data as a dict with all possible features.
        :return: The created CropRecommendation object.
        """
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        MODEL_DIR = os.path.join(BASE_DIR, 'ml_models')

        try:
            crop_model = joblib.load(os.path.join(MODEL_DIR, 'crop_model.pkl'))
            crop_encoder = joblib.load(os.path.join(MODEL_DIR, 'Crop_label_encoder.pkl'))
        except Exception as e:
            print(f"Error loading crop model or label encoder: {e}")
            return None

        crop_feature_names = ['Nitrogen', 'Phosphorus', 'Potassium', 'Temperature', 'Humidity', 'pH', 'Rainfall']
        input_dict = {k: input_data.get(k, 0) for k in crop_feature_names}

        crop_df = pd.DataFrame([input_dict])
        crop_prediction = crop_model.predict(crop_df)[0]
        crop_predicted = crop_encoder.inverse_transform([crop_prediction])[0]

        # Safety for phosphorous
        phosphorous = input_dict.get('Phosphorus', 0)

        # Create a copy of the original input data for farmer_inputs
        farmer_inputs = {
            'soil_type': input_data.get('Soil_type', ''),
            'nitrogen': input_dict.get('Nitrogen', 0),
            'phosphorous': phosphorous,
            'potassium': input_dict.get('Potassium', 0),
            'ph_value': input_dict.get('pH', 0),
            'temperature': input_dict.get('Temperature', 0),
            'humidity': input_dict.get('Humidity', 0),
            'rainfall': input_dict.get('Rainfall', 0),
            'moisture': input_data.get('Moisture', 0),
        }

        # Create AI outputs with the prediction result
        ai_outputs = {
            'crop_predicted': crop_predicted,
            'confidence': 0.95,  # You can add actual confidence if available
        }

        recommendation = CropRecommendation.objects.create(
            user=user,
            temperature=input_dict.get('Temperature', 0),
            humidity=input_dict.get('Humidity', 0),
            moisture=input_data.get('Moisture', 0),
            soil_type=input_data.get('Soil_type', ''),
            nitrogen=input_dict.get('Nitrogen', 0),
            potassium=input_dict.get('Potassium', 0),
            phosphorous=phosphorous,
            crop_predicted=crop_predicted,
            fertilizer_predicted='',
            # Save farmer inputs and AI outputs
            farmer_inputs=farmer_inputs,
            ai_outputs=ai_outputs,
            status='pending_review'
        )
        return recommendation

    @staticmethod
    def predict_and_save_recommendation(user, input_data):
        """
        Predict crop and fertilizer recommendations based on the input data and save them to the database.
        :param user: The user requesting the recommendation (instance of User model).
        :param input_data: Input data as a dict with all possible features.
        :return: The created CropRecommendation object.
        """
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        MODEL_DIR = os.path.join(BASE_DIR, 'ml_models')
        
        try:
            # Load models and label encoders
            crop_model = joblib.load(os.path.join(MODEL_DIR, 'crop_model.pkl'))
            fertilizer_model = joblib.load(os.path.join(MODEL_DIR, 'best_model_fertilizer.pkl'))
            crop_encoder = joblib.load(os.path.join(MODEL_DIR, 'Crop_label_encoder.pkl'))
            fertilizer_encoder = joblib.load(os.path.join(MODEL_DIR, 'Fertilizer_label_encoder.pkl'))
        except Exception as e:
            print(f"Error loading models or label encoders: {e}")
            return None

        # Hardcoded feature names (must match training)
        crop_feature_names = ['Nitrogen', 'Phosphorus', 'Potassium', 'Temperature', 'Humidity', 'pH', 'Rainfall']
        fertilizer_feature_names = ['Soil_color_encoded', 'Nitrogen', 'Phosphorus', 'Potassium', 'pH', 'Rainfall', 'Temperature']

        # Prepare input dict with defaults
        input_dict = {k: input_data.get(k, 0) for k in set(crop_feature_names + fertilizer_feature_names)}

        # Ensure correct encoding for Soil_type using Fertilizer encoder
        if 'Soil_color_encoded' in input_dict and fertilizer_encoder is not None:
            try:
                input_dict['Soil_color_encoded'] = fertilizer_encoder.transform([input_dict['Soil_color_encoded']])[0]
            except Exception:
                input_dict['Soil_color_encoded'] = 0

        # Make sure the columns match what the model expects
        # DataFrame for crop model
        crop_df = pd.DataFrame([{k: input_dict.get(k, 0) for k in crop_feature_names}])
        # DataFrame for fertilizer model
        fertilizer_df = pd.DataFrame([{k: input_dict.get(k, 0) for k in fertilizer_feature_names}])

        # Predict crop
        crop_prediction = crop_model.predict(crop_df)[0]
        crop_predicted = crop_encoder.inverse_transform([crop_prediction])[0]

        # Predict fertilizer
        fertilizer_prediction = fertilizer_model.predict(fertilizer_df)[0]
        fertilizer_predicted = fertilizer_encoder.inverse_transform([fertilizer_prediction])[0]

        # Decode soil type for storage
        try:
            soil_type_decoded = fertilizer_encoder.inverse_transform([int(input_dict['Soil_color'])])[0]
        except Exception:
            soil_type_decoded = 'Unknown'

        # Safety for phosphorous
        phosphorous = input_dict.get('Phosphorus', 0)

        # Create farmer inputs
        farmer_inputs = {
            'soil_type': soil_type_decoded,
            'nitrogen': input_dict.get('Nitrogen', 0),
            'phosphorous': phosphorous,
            'potassium': input_dict.get('Potassium', 0),
            'ph_value': input_dict.get('pH', 0),
            'temperature': input_dict.get('Temperature', 0),
            'humidity': input_dict.get('Humidity', 0),
            'rainfall': input_dict.get('Rainfall', 0),
            'moisture': input_dict.get('Moisture', 0),
        }

        # Create AI outputs
        ai_outputs = {
            'crop_predicted': crop_predicted,
            'fertilizer_predicted': fertilizer_predicted,
            'confidence': 0.95,  # You can add actual confidence if available
        }

        # Create and save recommendation
        recommendation = CropRecommendation.objects.create(
            user=user,
            temperature=input_dict.get('Temperature', 0),
            humidity=input_dict.get('Humidity', 0),
            moisture=input_dict.get('Moisture', 0),
            soil_type=soil_type_decoded,  # Decode to actual soil type
            nitrogen=input_dict.get('Nitrogen', 0),
            potassium=input_dict.get('Potassium', 0),
            phosphorous=phosphorous,
            crop_predicted=crop_predicted,
            fertilizer_predicted=fertilizer_predicted,
            # Save farmer inputs and AI outputs
            farmer_inputs=farmer_inputs,
            ai_outputs=ai_outputs,
            status='pending_review'  
        )
        return recommendation