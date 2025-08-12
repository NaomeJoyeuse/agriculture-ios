import os
import joblib
import pandas as pd
from django.db import models
from .user import User

class InputUsage(models.Model):
    crop_type = models.CharField(max_length=100)
    soil_type = models.CharField(max_length=100)
    growth_stage = models.CharField(max_length=100)
    fertilizer_quantity = models.FloatField()
    application_timing = models.CharField(max_length=100)
    application_method = models.CharField(max_length=100)
    predicted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.crop_type} - {self.growth_stage} ({self.predicted_at})"

    @staticmethod
    def predict_and_save_input_usage(input_data):
        """
        Predict fertilizer quantity, application timing, and application method, then save to InputUsage.
        :param input_data: dict with all required features (real values provided by the user)
        :return: The created InputUsage object
        """
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        MODEL_DIR = os.path.join(BASE_DIR, 'aios_app', 'ml_models')
        try:
            # Load models and label encoders
            fertilizer_model = joblib.load(os.path.join(MODEL_DIR, 'fertilizer_quantity_model.pkl'))
            timing_model = joblib.load(os.path.join(MODEL_DIR, 'application_timing_model.pkl'))
            method_model = joblib.load(os.path.join(MODEL_DIR, 'application_method_model.pkl'))
            timing_encoder = joblib.load(os.path.join(MODEL_DIR, 'application_timing_label_encoder.pkl'))
            method_encoder = joblib.load(os.path.join(MODEL_DIR, 'application_method_label_encoder.pkl'))
            crop_encoder = joblib.load(os.path.join(MODEL_DIR, 'Crop_type_label_encoder.pkl'))
            growth_encoder = joblib.load(os.path.join(MODEL_DIR, 'growth_stages_label_encoder.pkl'))
        except Exception as e:
            print(f"Error loading models or encoders: {e}")
            return None

        # Encoding the real values (user input) to numeric values using label encoders
        try:
            crop_type_encoded = crop_encoder.transform([input_data['crop_type']])[0] if input_data['crop_type'] in crop_encoder.classes_ else 0
            growth_stage_encoded = growth_encoder.transform([input_data['growth_stage']])[0] if input_data['growth_stage'] in growth_encoder.classes_ else 0
        except Exception as e:
            print(f"Error during encoding: {e}")
            return None

        # Prepare model input: only numeric/encoded features
        model_feature_names = [
            'Crop Type_encoded', 'Soil_pH_num', 'Soil Type_encoded',
            'Fertilizer Recommendations_encoded', 'Fert_Quantity_num',
            'Application Timing_encoded', 'Application Method_encoded',
            'Planting_Density_num', 'Growth Stages_encoded'
        ]
        model_input_dict = {k: input_data.get(k, 0) for k in model_feature_names}
        X_df = pd.DataFrame([model_input_dict])

        # Predict
        fertilizer_quantity = fertilizer_model.predict(X_df)[0]
        timing_pred = timing_model.predict(X_df)[0]
        method_pred = method_model.predict(X_df)[0]
        # Decode timing and method
        application_timing = timing_encoder.inverse_transform([timing_pred])[0]
        application_method = method_encoder.inverse_transform([method_pred])[0]

        # Save to InputUsage
        usage = InputUsage.objects.create(
            crop_type=input_data.get('crop_type', ''),
            soil_type=input_data.get('soil_type', ''),
            growth_stage=input_data.get('growth_stage', ''),
            fertilizer_quantity=fertilizer_quantity,
            application_timing=application_timing,
            application_method=application_method
        )
        return usage
