
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..decorator import jwt_required
from ...serializer.recommendation_serializer import CropRecommendationSerializer
from ...models_db.recommendation import CropRecommendation
from aios_app.models_db.user import User
import os   
import joblib
from django.db.models import Q
def _uid(request):
    return getattr(getattr(request, 'user', None), 'id', None) or getattr(request, 'user_id', None)

@jwt_required
@api_view(['POST'])
def submit_recommendation(request):
    # farmer sends the recommendation payload to agronomist
    data = request.data.copy()
    ser = CropRecommendationSerializer(data=data, context={'request': request})
    if ser.is_valid():
        rec = ser.save(status='pending_review')  # enforce default
        return Response(CropRecommendationSerializer(rec).data, status=201)
    return Response(ser.errors, status=400)

@jwt_required
@api_view(['GET'])
def my_recommendations(request):
    uid = _uid(request)
    qs = CropRecommendation.objects.filter(user_id=uid).order_by('-timestamp')
    return Response(CropRecommendationSerializer(qs, many=True).data, status=200)

@jwt_required
@api_view(['GET'])
def agronomist_inbox(request):
    # You can also scope to only records with agronomist=None or agronomist=request.user
    qs = CropRecommendation.objects.filter(status__in=['pending_review', 'pending','in_review','translated']).order_by('-timestamp')
    return Response(CropRecommendationSerializer(qs, many=True).data, status=200)

@jwt_required
@api_view(['PATCH'])
def claim_recommendation(request, rec_id):
    uid = _uid(request)
    try:
        rec = CropRecommendation.objects.get(pk=rec_id)
    except CropRecommendation.DoesNotExist:
        return Response({'detail': 'Not found'}, status=404)
    rec.agronomist_id = uid
    rec.status = 'in_review'
    rec.save(update_fields=['agronomist_id', 'status'])
    return Response(CropRecommendationSerializer(rec).data, status=200)

@jwt_required
@api_view(['PATCH'])
def review_recommendation(request, rec_id):
    uid = _uid(request)
    try:
        rec = CropRecommendation.objects.get(pk=rec_id)
    except CropRecommendation.DoesNotExist:
        return Response({'detail': 'Not found'}, status=404)

    # Only the agronomist who claimed it can review it
    if rec.agronomist_id and rec.agronomist_id != uid:
        return Response({'detail': 'Not allowed'}, status=403)

    data = request.data.copy()
    
    print(f"Received data: {data}")
    
    new_status = (data.get('status') or 'translated').lower()
    if new_status not in ['in_review', 'translated', 'returned']:
        return Response({'detail': 'Invalid status'}, status=400)
    
    data['status'] = new_status
    data['agronomist_id'] = uid
    
    ser = CropRecommendationSerializer(rec, data=data, partial=True, context={'request': request})
    if ser.is_valid():
       
        rec = ser.save()
        print(f"Saved record: {CropRecommendationSerializer(rec).data}")
        return Response(CropRecommendationSerializer(rec).data, status=200)
    
    print(f"Validation errors: {ser.errors}")
    return Response(ser.errors, status=400)

@jwt_required
@api_view(['GET'])
def get_recommendation(request, rec_id):
    try:
        rec = CropRecommendation.objects.get(pk=rec_id)
    except CropRecommendation.DoesNotExist:
        return Response({'detail': 'Not found'}, status=404)
    return Response(CropRecommendationSerializer(rec).data, status=200)

@jwt_required
@api_view(['GET'])
def my_reviews(request):
    user = request.user
    print(f"🧪 Extracted user: {user}, ID: {user.id}")

    reviews = CropRecommendation.objects.filter(
        agronomist_id=user.id,
        status__in=["translated", "returned"]
    ).order_by('-timestamp')

    print(f"✅ Found my reviews: {reviews.count()}")
    for r in reviews:
        print(f"ID: {r.id}, Status: {r.status}, Agronomist: {r.agronomist_id}")

    return Response(CropRecommendationSerializer(reviews, many=True).data)
def _uid(request):
    return getattr(getattr(request, 'user', None), 'id', None) or getattr(request, 'user_id', None)

@jwt_required
@api_view(['POST'])
def create_crop_only_prediction(request):
    """
    Handle POST request to create a new crop-only recommendation (no fertilizer prediction).
    """
    user_id = _uid(request)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

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


@jwt_required
@api_view(['POST'])
def create_prediction(request):
    """
    Handle POST request to create a crop and fertilizer recommendation.
    """
    user_id = _uid(request)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

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
        'Temperature': request.data.get('temperature'),
    }

    recommendation = CropRecommendation.predict_and_save_recommendation(user, input_data)

    if recommendation is not None:
        serializer = CropRecommendationSerializer(recommendation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response({"error": "Crop and fertilizer prediction failed."}, status=status.HTTP_400_BAD_REQUEST)    
    
from django.db.models import Q

@api_view(['GET'])
@jwt_required
def all_recommendations_for_agronomist(request):
    """
    Fetch all recommendations where:
    - status is actionable for agronomist
    - agronomist is None (waiting to claim) OR it's me
    """
    
    # Use the _uid helper function like other views
    uid = _uid(request)
    
    # Get the user object if needed
    try:
        user = User.objects.get(pk=uid)
    except User.DoesNotExist:
        return Response({'detail': 'User not found'}, status=404)
    
    qs = CropRecommendation.objects.filter(
        status__in=["pending_review", "in_review", "translated", "returned"]
    ).filter(
        Q(agronomist=None) | Q(agronomist=user)
    ).order_by('-timestamp')

    return Response(CropRecommendationSerializer(qs, many=True).data)   