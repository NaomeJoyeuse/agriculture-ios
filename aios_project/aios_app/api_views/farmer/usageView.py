from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count, Avg
from ..decorator import jwt_required
from ...serializer.usageSerilaizer import UsageSerializer
from ...models_db.usage import Usage

def _uid(request):
    return getattr(getattr(request, 'user', None), 'id', None) or getattr(request, 'user_id', None)

def _role(user):
    return str(getattr(user, 'role', '')).lower()

@jwt_required
@api_view(['GET'])
def list_my_usages(request):
    """
    Get all input usage records for the current user
    """
    uid = _uid(request)
    
    # Apply filters
    queryset = Usage.objects.filter(farmer_id=uid).order_by('-application_date')
    
    # Filter by input type
    input_type = request.query_params.get('input_type')
    if input_type:
        queryset = queryset.filter(input_type=input_type)
    
    # Filter by season
    season_year = request.query_params.get('season_year')
    if season_year:
        queryset = queryset.filter(season_year=season_year)
    
    season_name = request.query_params.get('season_name')
    if season_name:
        queryset = queryset.filter(season_name=season_name)
    
    # Filter by crop
    crop = request.query_params.get('crop')
    if crop:
        queryset = queryset.filter(crop=crop)
    
    # Date range filters
    start_date = request.query_params.get('start_date')
    if start_date:
        queryset = queryset.filter(application_date__gte=start_date)
    
    end_date = request.query_params.get('end_date')
    if end_date:
        queryset = queryset.filter(application_date__lte=end_date)
    
    return Response(UsageSerializer(queryset, many=True).data, status=200)

@jwt_required
@api_view(['POST'])
def create_usage(request):
    """
    Create a new input usage record for the current user
    """
    uid = _uid(request)
    
    data = request.data.copy()
    # Set the farmer to the current user
    data['farmer'] = uid
    
    serializer = UsageSerializer(data=data)
    if serializer.is_valid():
        usage = serializer.save()
        return Response(UsageSerializer(usage).data, status=201)
    return Response(serializer.errors, status=400)

@jwt_required
@api_view(['GET'])
def get_usage(request, usage_id):
    """
    Get a specific input usage record
    """
    uid = _uid(request)
    role = _role(request.user)
    
    try:
        usage = Usage.objects.get(pk=usage_id)
        
        # Check permissions - only owner or admin/agronomist can view
        if str(usage.farmer_id) != str(uid) and role not in ['admin', 'agronomist']:
            return Response({'detail': 'Not allowed'}, status=403)
            
        return Response(UsageSerializer(usage).data, status=200)
    except Usage.DoesNotExist:
        return Response({'detail': 'Usage record not found'}, status=404)

@jwt_required
@api_view(['PATCH', 'PUT'])
def update_usage(request, usage_id):
    """
    Update an input usage record
    """
    uid = _uid(request)
    
    try:
        usage = Usage.objects.get(pk=usage_id)
        
        # Only the owner can update
        if str(usage.farmer_id) != str(uid):
            return Response({'detail': 'Not allowed'}, status=403)
        
        serializer = UsageSerializer(usage, data=request.data, partial=True)
        if serializer.is_valid():
            updated_usage = serializer.save()
            return Response(UsageSerializer(updated_usage).data, status=200)
        return Response(serializer.errors, status=400)
    except Usage.DoesNotExist:
        return Response({'detail': 'Usage record not found'}, status=404)

@jwt_required
@api_view(['DELETE'])
def delete_usage(request, usage_id):
    """
    Delete an input usage record
    """
    uid = _uid(request)
    role = _role(request.user)
    
    try:
        usage = Usage.objects.get(pk=usage_id)
        
        # Only owner or admin can delete
        if str(usage.farmer_id) != str(uid) and role != 'admin':
            return Response({'detail': 'Not allowed'}, status=403)
        
        usage.delete()
        return Response(status=204)
    except Usage.DoesNotExist:
        return Response({'detail': 'Usage record not found'}, status=404)

@jwt_required
@api_view(['GET'])
def usage_summary(request):
    """
    Get summary statistics for input usage
    """
    uid = _uid(request)
    role = _role(request.user)
    
    # Determine which records to include based on role
    if role in ['admin', 'agronomist']:
        # Admins and agronomists can see all records or filter by farmer
        farmer_id = request.query_params.get('farmer_id')
        if farmer_id:
            queryset = Usage.objects.filter(farmer_id=farmer_id)
        else:
            queryset = Usage.objects.all()
    else:
        # Regular users can only see their own records
        queryset = Usage.objects.filter(farmer_id=uid)
    
    # Apply filters
    input_type = request.query_params.get('input_type')
    if input_type:
        queryset = queryset.filter(input_type=input_type)
    
    season_year = request.query_params.get('season_year')
    if season_year:
        queryset = queryset.filter(season_year=season_year)
    
    season_name = request.query_params.get('season_name')
    if season_name:
        queryset = queryset.filter(season_name=season_name)
    
    crop = request.query_params.get('crop')
    if crop:
        queryset = queryset.filter(crop=crop)
    
    # Date range filters
    start_date = request.query_params.get('start_date')
    if start_date:
        queryset = queryset.filter(application_date__gte=start_date)
    
    end_date = request.query_params.get('end_date')
    if end_date:
        queryset = queryset.filter(application_date__lte=end_date)
    
    # Get grouping (default: season + input_type)
    group_by = request.query_params.get('group_by', 'season_year,season_name,input_type')
    group_fields = [field.strip() for field in group_by.split(',') if field.strip()]
    
    # Validate group fields
    valid_fields = ['season_year', 'season_name', 'input_type', 'crop', 'unit']
    for field in group_fields:
        if field not in valid_fields:
            return Response(
                {"error": f"Invalid group_by field: {field}. Valid fields are: {', '.join(valid_fields)}"},
                status=400
            )
    
    # Default grouping if none specified
    if not group_fields:
        group_fields = ['season_year', 'season_name', 'input_type']
    
    # Perform aggregation
    aggregated = (
        queryset.values(*group_fields)
        .annotate(
            total_quantity=Sum('quantity'),
            total_cost=Sum('cost'),
            avg_cost=Avg('cost'),
            count=Count('id'),
        )
        .order_by(*group_fields)
    )
    
    return Response({
        "group_by": group_fields,
        "results": list(aggregated)
    }, status=200)

@jwt_required
@api_view(['GET'])
def list_all_usages(request):
    """
    Admin/Agronomist endpoint to list all usage records
    """
    role = _role(request.user)
    if role not in ['admin', 'agronomist']:
        return Response({'detail': 'Not allowed'}, status=403)
    
    queryset = Usage.objects.all().order_by('-application_date')
    
    # Apply filters (same as list_my_usages)
    input_type = request.query_params.get('input_type')
    if input_type:
        queryset = queryset.filter(input_type=input_type)
    
    season_year = request.query_params.get('season_year')
    if season_year:
        queryset = queryset.filter(season_year=season_year)
    
    season_name = request.query_params.get('season_name')
    if season_name:
        queryset = queryset.filter(season_name=season_name)
    
    crop = request.query_params.get('crop')
    if crop:
        queryset = queryset.filter(crop=crop)
    
    farmer_id = request.query_params.get('farmer_id')
    if farmer_id:
        queryset = queryset.filter(farmer_id=farmer_id)
    
    # Date range filters
    start_date = request.query_params.get('start_date')
    if start_date:
        queryset = queryset.filter(application_date__gte=start_date)
    
    end_date = request.query_params.get('end_date')
    if end_date:
        queryset = queryset.filter(application_date__lte=end_date)
    
    return Response(UsageSerializer(queryset, many=True).data, status=200)