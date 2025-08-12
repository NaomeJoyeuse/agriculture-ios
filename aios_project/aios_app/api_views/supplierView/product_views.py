# # aios_app/api_views/product_api.py

# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework import status

# from ...models_db.supplier import Product, Supplier
# from ...models_db.user import User
# from ...serializer.product_serilizer import ProductSerializer
# from ..decorator import jwt_required


# @jwt_required
# @api_view(['POST'])
# def create_product(request):
#     """
#     Handle POST request to create a new product linked to a supplier.
#     Requires supplier ID and JWT auth header.
#     """
#     supplier_id = request.data.get('supplier')

#     # 1. Check if supplier ID provided
#     if not supplier_id:
#         return Response(
#             {"error": "Supplier ID is required."},
#             status=status.HTTP_400_BAD_REQUEST
#         )

#     # 2. Check if supplier exists
#     try:
#         supplier = User.objects.get(id=supplier_id)
#     except Supplier.DoesNotExist:
#         return Response(
#             {"error": f"Supplier with ID {supplier_id} does not exist."},
#             status=status.HTTP_404_NOT_FOUND
#         )

#     # 3. Validate and save product
#     serializer = ProductSerializer(data=request.data)
#     if serializer.is_valid():   
#         product = serializer.save()
#         return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)

#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @jwt_required
# @api_view(['GET'])
# def list_products(request):
#     """
#     Get a list of all products.
#     """
#     products = Product.objects.all()
#     serializer = ProductSerializer(products, many=True)
#     return Response(serializer.data, status=status.HTTP_200_OK)

# @jwt_required
# @api_view(['GET'])
# def get_product(request, product_id):
#     """
#     Get a single product by ID.
#     """
#     try:
#         product = Product.objects.get(id=product_id)
#     except Product.DoesNotExist:
#         return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

#     serializer = ProductSerializer(product)
#     return Response(serializer.data, status=status.HTTP_200_OK)

# @jwt_required
# @api_view(['GET'])
# def list_products_by_supplier(request, supplier_id):
#     """
#     Get all products belonging to one supplier.
#     """
#     try:
#         User.objects.get(id=supplier_id)
#     except User.DoesNotExist:
#         return Response({"error": "Supplier not found."}, status=status.HTTP_404_NOT_FOUND)

#     products = Product.objects.filter(supplier_id=supplier_id)
#     serializer = ProductSerializer(products, many=True)
#     return Response(serializer.data, status=status.HTTP_200_OK)

# aios_app/api_views/product_api.py

from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from ...models_db.supplier import Product
from ...models_db.user import User
from ...serializer.product_serilizer import ProductSerializer
from ..decorator import jwt_required


@jwt_required
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])  # allow file uploads
def create_product(request):
    """
    Handle POST request to create a new product linked to a supplier (User).
    Requires supplier ID and JWT auth header.
    """
    supplier_id = request.data.get('supplier')

    # 1) Check if supplier ID provided
    if not supplier_id:
        return Response({"error": "Supplier ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    # 2) Check if supplier (User) exists
    try:
        User.objects.get(id=supplier_id)
    except User.DoesNotExist:  # fixed: was Supplier.DoesNotExist
        return Response({"error": f"Supplier with ID {supplier_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)

    # 3) Validate and save product
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        product = serializer.save()
        return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@jwt_required
@api_view(['GET'])
def list_products(request):
    """
    Get a list of all products.
    """
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@jwt_required
@api_view(['GET', 'PATCH', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser])  # allow multipart for update
def product_detail(request, product_id):
    """
    GET    /products/<id>/       -> retrieve one
    PATCH  /products/<id>/       -> partial update
    PUT    /products/<id>/       -> full update
    DELETE /products/<id>/       -> delete
    """
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    # Optional: enforce ownership (requires your jwt_required to attach user or user_id)
    request_user_id = getattr(getattr(request, 'user', None), 'id', None) or getattr(request, 'user_id', None)
    if request.method in ['PATCH', 'PUT', 'DELETE'] and request_user_id:
        if product.supplier_id != int(request_user_id):
            return Response({"error": "You are not allowed to modify this product."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        return Response(ProductSerializer(product).data, status=status.HTTP_200_OK)

    if request.method in ['PATCH', 'PUT']:
        partial = request.method == 'PATCH'
        data = request.data.copy()

        # If supplier is provided, validate it (or you can disallow changing supplier)
        if 'supplier' in data and str(data['supplier']).strip():
            try:
                User.objects.get(id=data['supplier'])
            except User.DoesNotExist:
                return Response({"error": "Supplier not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, data=data, partial=partial)
        if serializer.is_valid():
            product = serializer.save()
            return Response(ProductSerializer(product).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@jwt_required
@api_view(['GET'])
def list_products_by_supplier(request, supplier_id):
    """
    Get all products belonging to one supplier (User).
    """
    try:
        User.objects.get(id=supplier_id)
    except User.DoesNotExist:
        return Response({"error": "Supplier not found."}, status=status.HTTP_404_NOT_FOUND)

    products = Product.objects.filter(supplier_id=supplier_id)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)