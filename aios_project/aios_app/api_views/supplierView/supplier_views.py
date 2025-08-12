
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