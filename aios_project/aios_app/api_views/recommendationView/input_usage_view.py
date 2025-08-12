# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework import status
# from aios_app.models_db.input_usage import InputUsage
# from aios_app.serializer.inputUsage_serializer import InputUsageSerializer
# import joblib
# import os
# import numpy as np

# @api_view(['POST'])
# def predict_input_usage(request):
#     """
#     Handle POST request to predict and save input usage recommendation.
#     Expects user-friendly inputs: crop_type, soil_type, growth_stage, soil_pH, planting_density.
#     """
#     # Extract user-friendly inputs
#     crop_type = request.data.get('crop_type')
#     soil_type = request.data.get('soil_type')
#     growth_stage = request.data.get('growth_stage')
#     soil_pH = request.data.get('soil_pH')
#     planting_density = request.data.get('planting_density')

#     # Load label encoders
#     BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     MODEL_DIR = os.path.join(BASE_DIR, 'ml_models')
#     try:
#         crop_encoder = joblib.load(os.path.join(MODEL_DIR, 'Crop_type_label_encoder.pkl'))
#         soil_encoder = joblib.load(os.path.join(MODEL_DIR, 'Soil Type_label_encoder.pkl'))
#         growth_stage_encoder = joblib.load(os.path.join(MODEL_DIR, 'growth_stages_label_encoder.pkl'))
#         fert_rec_encoder = joblib.load(os.path.join(MODEL_DIR, 'fertilizer_recommendations_label_encoder.pkl'))
#         timing_encoder = joblib.load(os.path.join(MODEL_DIR, 'application_timing_label_encoder.pkl'))
#         method_encoder = joblib.load(os.path.join(MODEL_DIR, 'application_method_label_encoder.pkl'))
#     except Exception as e:
#         return Response({'error': f'Error loading encoders: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     # Encode user inputs
#     try:
#         crop_type_encoded = int(crop_encoder.transform([crop_type])[0])
#         soil_type_encoded = int(soil_encoder.transform([soil_type])[0])
#         growth_stage_encoded = int(growth_stage_encoder.transform([growth_stage])[0])
#     except Exception as e:
#         return Response({'error': f'Error encoding input: {e}'}, status=status.HTTP_400_BAD_REQUEST)

#     # For features not provided by user, use a default or placeholder (e.g., 0 or most common value)
#     # You can improve this by looking up defaults from your CSV if needed
#     input_data = {
#         'Crop Type_encoded': crop_type_encoded,
#         'Soil_pH_num': float(soil_pH) if soil_pH is not None else 6.0,
#         'Soil Type_encoded': soil_type_encoded,
#         'Fertilizer Recommendations_encoded': 0,  # Placeholder, can be improved
#         'Fert_Quantity_num': 0,  # Placeholder, not used for prediction
#         'Application Timing_encoded': 0,  # Placeholder, not used for prediction
#         'Application Method_encoded': 0,  # Placeholder, not used for prediction
#         'Planting_Density_num': float(planting_density) if planting_density is not None else 50000,
#         'Growth Stages_encoded': growth_stage_encoded,
#         'crop_type': crop_type,
#         'soil_type': soil_type,
#         'growth_stage': growth_stage
#     }

#     usage_instance = InputUsage.predict_and_save_input_usage(input_data)
#     if usage_instance:
#         # Decode the output fields if needed (already decoded in model method)
#         serializer = InputUsageSerializer(usage_instance)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     else:
#         return Response({'error': 'Prediction failed.'}, status=status.HTTP_400_BAD_REQUEST)



from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from aios_app.models_db.input_usage import InputUsage
from aios_app.serializer.inputUsage_serializer import InputUsageSerializer
import joblib
import os
import numpy as np

@api_view(['POST'])
def predict_input_usage(request):
    """
    Handle POST request to predict and save input usage recommendation.
    Expects user-friendly inputs: crop_type, soil_type, growth_stage, soil_pH, planting_density.
    """
    # Extract user-friendly inputs
    crop_type = request.data.get('crop_type')
    soil_type = request.data.get('soil_type')
    growth_stage = request.data.get('growth_stage')
    soil_pH = request.data.get('soil_pH')
    planting_density = request.data.get('planting_density')

    # Load label encoders
    MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'ml_models')
    
    # Debug: Print the model directory path
    print(f"Loading encoders from: {MODEL_DIR}")

    try:
        crop_encoder = joblib.load(os.path.join(MODEL_DIR, 'Crop_type_label_encoder.pkl'))
        soil_encoder = joblib.load(os.path.join(MODEL_DIR, 'soil_type_label_encoder.pkl'))
        growth_stage_encoder = joblib.load(os.path.join(MODEL_DIR, 'growth_stages_label_encoder.pkl'))
        fert_rec_encoder = joblib.load(os.path.join(MODEL_DIR, 'fertilizer_recommendations_label_encoder.pkl'))
        timing_encoder = joblib.load(os.path.join(MODEL_DIR, 'application_timing_label_encoder.pkl'))
        method_encoder = joblib.load(os.path.join(MODEL_DIR, 'application_method_label_encoder.pkl'))
    except Exception as e:
        return Response({'error': f'Error loading encoders: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Encode user inputs
    try:
        crop_type_encoded = crop_encoder.transform([crop_type])[0] if crop_type in crop_encoder.classes_ else 0
        soil_type_encoded = soil_encoder.transform([soil_type])[0] if soil_type in soil_encoder.classes_ else 0
        growth_stage_encoded = growth_stage_encoder.transform([growth_stage])[0] if growth_stage in growth_stage_encoder.classes_ else 0
    except Exception as e:
        return Response({'error': f'Error encoding input: {e}'}, status=status.HTTP_400_BAD_REQUEST)

    # For features not provided by user, use a default or placeholder (e.g., 0 or most common value)
    # You can improve this by looking up defaults from your CSV if needed
    input_data = {
        'Crop Type_encoded': crop_type_encoded,
        'Soil_pH_num': float(soil_pH) if soil_pH is not None else 6.0,
        'Soil Type_encoded': soil_type_encoded,
        'Fertilizer Recommendations_encoded': 0,  # Placeholder, can be improved
        'Fert_Quantity_num': 0,  # Placeholder, not used for prediction
        'Application Timing_encoded': 0,  # Placeholder, not used for prediction
        'Application Method_encoded': 0,  # Placeholder, not used for prediction
        'Planting_Density_num': float(planting_density) if planting_density is not None else 50000,
        'Growth Stages_encoded': growth_stage_encoded,
        'crop_type': crop_type,
        'soil_type': soil_type,
        'growth_stage': growth_stage
    }

    usage_instance = InputUsage.predict_and_save_input_usage(input_data)
    if usage_instance:
        # Decode the output fields if needed (already decoded in model method)
        serializer = InputUsageSerializer(usage_instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response({'error': 'Prediction failed.'}, status=status.HTTP_400_BAD_REQUEST)
