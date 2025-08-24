from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..decorator import jwt_required
from ...serializer.farmerSerilaizer import FarmerSerializer
from ...models_db.farmer import Farmer
from ...models_db.user import User

def _uid(request):
    return getattr(getattr(request, 'user', None), 'id', None) or getattr(request, 'user_id', None)

def _role(user):
    return str(getattr(user, 'role', '')).lower()

@jwt_required
@api_view(['GET'])
def my_farmer_profile(request):
    uid = _uid(request)
    try:
        farmer = Farmer.objects.get(user_id=uid)
    except Farmer.DoesNotExist:
        return Response({'detail': 'Profile not found'}, status=404)
    return Response(FarmerSerializer(farmer).data, status=200)

@jwt_required
@api_view(['POST'])
def create_my_farmer_profile(request):
    """
    Create a farmer profile for the current user
    """
    user = request.user
    if Farmer.objects.filter(user_id=user.id).exists():
        return Response({'detail': 'Profile already exists'}, status=400)

    data = request.data.copy()
    # Don't override the user ID if it's already in the request data
    if 'user' not in data:
        data['user'] = user.id
    ser = FarmerSerializer(data=data)
    if ser.is_valid():
        farmer = ser.save()
        return Response(FarmerSerializer(farmer).data, status=201)
    return Response(ser.errors, status=400) 

@jwt_required
@api_view(['PATCH'])
def update_my_farmer_profile(request):
    uid = _uid(request)
    try:
        farmer = Farmer.objects.get(user_id=uid)
    except Farmer.DoesNotExist:
        return Response({'detail': 'Profile not found'}, status=404)

    ser = FarmerSerializer(farmer, data=request.data, partial=True)
    if ser.is_valid():
        farmer = ser.save()
        return Response(FarmerSerializer(farmer).data, status=200)
    return Response(ser.errors, status=400)


@jwt_required
@api_view(['GET'])
def list_farmers(request):
    # Allow only certain roles to list (adjust as needed)
    role = _role(request.user)
    # if role not in ['admin', 'leader']:
    #     return Response({'detail': 'Not allowed'}, status=403)

    qs = Farmer.objects.select_related('user').order_by('-created_at')
    return Response(FarmerSerializer(qs, many=True).data, status=200)

@jwt_required
@api_view(['GET'])
def get_farmer(request, farmer_id):
    role = _role(request.user)
    # if role not in ['admin', 'leader']:
    #     return Response({'detail': 'Not allowed'}, status=403)
    try:
        farmer = Farmer.objects.get(pk=farmer_id)
    except Farmer.DoesNotExist:
        return Response({'detail': 'Not found'}, status=404)
    return Response(FarmerSerializer(farmer).data, status=200)