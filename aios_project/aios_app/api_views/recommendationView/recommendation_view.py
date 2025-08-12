from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from aios_app.serializer.recommendation_serializer import CropRecommendationSerializer
from aios_app.models_db.recommendation import CropRecommendation  # type: ignore
from aios_app.models_db.user import User
from aios_app.api_views.decorator import jwt_required
import joblib
import os


@jwt_required
@api_view(['POST'])
def create_recommendation(request):
    """
    Handle POST request to create a new crop recommendation.
    """
    serializer = CropRecommendationSerializer(data=request.data)

    if serializer.is_valid():
        # Save the recommendation to the database
        recommendation = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@jwt_required
@api_view(['GET'])
def get_recommendations(request):
    """
    Handle GET request to retrieve crop recommendations.
    """
    recommendations = CropRecommendation.objects.all()  # type: ignore
    serializer = CropRecommendationSerializer(recommendations, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
    
@jwt_required   
@api_view(['POST'])
def create_prediction(request):
    """
    Handle POST request to create a new crop and fertilizer recommendation.
    """
    user_id = request.user_id  # Extracted from JWT token

    try:
        # Retrieve the user from the database using the user_id
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    # Encode soil_type to Soil_color_encoded using the label encoder
    soil_type = request.data.get('soil_type')
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL_DIR = os.path.join(BASE_DIR, 'ml_models')
    try:
        soil_encoder = joblib.load(os.path.join(MODEL_DIR, 'Soil_color_label_encoder.pkl'))
        soil_color_encoded = soil_encoder.transform([soil_type])[0] if soil_type else 0
    except Exception:
        soil_color_encoded = 0

    input_data = {
        'Soil_color_encoded': soil_color_encoded,
        'Nitrogen': request.data.get('nitrogen'),
        'Phosphorus': request.data.get('phosphorous'),
        'Potassium': request.data.get('potassium'),
        'pH': request.data.get('ph_value'),
        'Rainfall': request.data.get('rainfall'),
        'Temperature': request.data.get('temperature')
    }
    
    
    # user = request.user  
    
    # Call the method to predict and save the recommendation
    recommendation = CropRecommendation.predict_and_save_recommendation(user, input_data)
    
    if recommendation is not None:
        # Serialize and return the recommendation data
        serializer = CropRecommendationSerializer(recommendation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response({"error": "Prediction failed."}, status=status.HTTP_400_BAD_REQUEST)

@jwt_required
@api_view(['POST'])
def create_crop_only_prediction(request):
    """
    Handle POST request to create a new crop-only recommendation (no fertilizer prediction).
    """
    user_id = request.user_id  # Extracted from JWT token

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    # Prepare input data for crop-only prediction
    input_data = {
        'Nitrogen': request.data.get('nitrogen'),
        'Phosphorus': request.data.get('phosphorous'),
        'Potassium': request.data.get('potassium'),
        'Temperature': request.data.get('temperature'),
        'Humidity': request.data.get('humidity'),
        'pH': request.data.get('ph_value'),
        'Rainfall': request.data.get('rainfall'),
        'Moisture': request.data.get('moisture'),
        'Soil_type': request.data.get('soil_type'),
    }

    recommendation = CropRecommendation.predict_and_save_crop_only(user, input_data)

    if recommendation is not None:
        serializer = CropRecommendationSerializer(recommendation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response({"error": "Crop-only prediction failed."}, status=status.HTTP_400_BAD_REQUEST)