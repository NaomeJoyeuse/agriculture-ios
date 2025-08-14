
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from ...models_db.supplier import Supplier 
from ...models_db.user import User
from ...serializer.supplierSerializer import SupplierSerializer
from ..decorator import jwt_required

@jwt_required
@api_view(['POST'])
def create_supplier(request):
    """
    Handle POST request to create a new supplier.
    Requires JWT authentication.
    """
    user_id = request.data.get('user')

    # ✅ 1. Check if user is provided
    if not user_id:
        return Response(
            {"error": "User ID is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # ✅ 2. Check if user exists
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {"error": f"User with ID {user_id} does not exist."},
            status=status.HTTP_404_NOT_FOUND
        )

    # ✅ 3. Continue with normal creation
    serializer = SupplierSerializer(data=request.data)

    if serializer.is_valid():
        supplier = serializer.save()
        return Response(SupplierSerializer(supplier).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@jwt_required
@api_view(['GET'])
def list_suppliers(request):
    """
    Get a list of all suppliers.
    Requires JWT authentication.
    """
    suppliers = Supplier.objects.all()
    serializer = SupplierSerializer(suppliers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@jwt_required
@api_view(['GET'])
def get_supplier(request, supplier_id):
    """
    Get a single supplier by ID.
    """
    try:
        supplier = Supplier.objects.get(user=supplier_id)
        serializer = SupplierSerializer(supplier)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Supplier.DoesNotExist:
        return Response({'error': 'Supplier not found'}, status=status.HTTP_404_NOT_FOUND)

@jwt_required
@api_view(['PATCH'])
def update_supplier(request, supplier_id):
    """
    Update a supplier by user_id (partial update).
    """
    try:
        supplier = Supplier.objects.get(user=supplier_id)
    except Supplier.DoesNotExist:
        return Response({'error': 'Supplier not found'}, status=status.HTTP_404_NOT_FOUND)
    data = request.data.copy()
# Do not allow changing the linked user
    data.pop('user', None)
    serializer = SupplierSerializer(supplier, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH'])
def supplier_by_user(request, user_id):
    """
    GET: fetch supplier by user_id
    PATCH: update supplier by user_id (partial update)
    """
    supplier = Supplier.objects.filter(user_id=user_id).first()
    if not supplier:
        return Response({'error': 'Supplier not found'}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        return Response(SupplierSerializer(supplier).data, status=status.HTTP_200_OK)
    if request.method == 'GET':
            return Response(SupplierSerializer(supplier).data, status=status.HTTP_200_OK)
    if request.method == 'GET':
             return Response(SupplierSerializer(supplier).data, status=status.HTTP_200_OK)

    data = request.data.copy()
    data.pop('user', None)  # do not allow changing linked user
    serializer = SupplierSerializer(supplier, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)