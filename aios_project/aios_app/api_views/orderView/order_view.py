from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from ...models_db.order import Order, OrderItem
from ...models_db.user import User
from ...models_db.supplier import Supplier, Product
from ...serializer.order_serializer import OrderSerializer, OrderItemSerializer
from ..decorator import jwt_required
from collections import defaultdict
from decimal import Decimal
from django.db import transaction
@jwt_required
@api_view(['POST'])
def create_order(request):
    """ 
    Create a new order with items.
    """
    user_id = request.data.get('user')
    supplier_id = request.data.get('supplier')
    items_data = request.data.get('items')

    # 1. Check required fields
    if not user_id or not supplier_id or not items_data:
        return Response(
            {"error": "user, supplier, and items are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 2. Check if user and supplier exist
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": f"User with ID {user_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)
    try:
        supplier = Supplier.objects.get(id=supplier_id)
    except Supplier.DoesNotExist:
        return Response({"error": f"Supplier with ID {supplier_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)

    # 3. Validate and save order
    serializer = OrderSerializer(data=request.data)
    if serializer.is_valid():
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@jwt_required
@api_view(['GET'])
def list_orders(request):
    """
    List all orders (with items).
    """
    orders = Order.objects.all().order_by('-orderDate')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@jwt_required
@api_view(['GET'])
def get_order(request, order_id):
    """
    Get a single order by ID (with items).
    """
    try:
        order = Order.objects.get(orderID=order_id)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = OrderSerializer(order)
    return Response(serializer.data, status=status.HTTP_200_OK)

@jwt_required
@api_view(['GET'])
def get_cart(request):
    # Single global cart per user: supplier=None, status='cart'
    user = getattr(request, 'user', None)
    if not user or not getattr(user, 'id', None):
        return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    cart, _ = Order.objects.get_or_create(user_id=user.id, status='cart', supplier=None)
    serializer = OrderSerializer(cart)
    return Response(serializer.data, status=status.HTTP_200_OK)

@jwt_required
@api_view(['POST'])
def add_cart_item(request):
    """
    body: { product: <id>, quantity: <int> }
    """
    user = getattr(request, 'user', None)
    if not user or not getattr(user, 'id', None):
        return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    product_id = request.data.get('product')
    try:
        quantity = int(request.data.get('quantity') or 1)
    except (TypeError, ValueError):
        quantity = 1

    if not product_id or quantity <= 0:
        return Response({'error': 'product and positive quantity are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    cart, _ = Order.objects.get_or_create(user_id=user.id, status='cart', supplier=None)
    item, created = OrderItem.objects.get_or_create(order=cart, product=product, defaults={'quantity': quantity})
    if not created:
        item.quantity += quantity
        item.save()

    serializer = OrderSerializer(cart)
    return Response(serializer.data, status=status.HTTP_200_OK)

@jwt_required
@api_view(['PATCH'])
def update_cart_item(request, item_id):
    """
    body: { quantity: <int> } ; if quantity <= 0 -> remove item
    """
    user = getattr(request, 'user', None)
    if not user or not getattr(user, 'id', None):
        return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        item = OrderItem.objects.select_related('order').get(
            id=item_id,
            order__status='cart',
            order__user_id=user.id,
            order__supplier__isnull=True
        )
    except OrderItem.DoesNotExist:
        return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        qty = int(request.data.get('quantity', 0))
    except (TypeError, ValueError):
        qty = 0

    if qty <= 0:
        order = item.order
        item.delete()
        cart = order
    else:
        item.quantity = qty
        item.save()
        cart = item.order

    serializer = OrderSerializer(cart)
    return Response(serializer.data, status=status.HTTP_200_OK)


@jwt_required
@api_view(['DELETE'])
def remove_cart_item(request, item_id):
    user = getattr(request, 'user', None)
    if not user or not getattr(user, 'id', None):
        return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        item = OrderItem.objects.select_related('order').get(
            id=item_id,
            order__status='cart',
            order__user_id=user.id,
            order__supplier__isnull=True
        )
    except OrderItem.DoesNotExist:
        return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

    cart = item.order
    item.delete()

    serializer = OrderSerializer(cart)
    return Response(serializer.data, status=status.HTTP_200_OK)


@jwt_required
@api_view(['POST'])
def checkout_cart(request):
    """
    Split a global cart (supplier=None, status='cart') into one pending order per supplier.
    Returns a list of created orders.
    """
    user = getattr(request, 'user', None)
    if not user or not getattr(user, 'id', None):
        return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        cart = Order.objects.select_related('user').prefetch_related('items__product').get(
            user_id=user.id, status='cart', supplier__isnull=True
        )
    except Order.DoesNotExist:
        return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

    if not cart.items.exists():
        return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

    # Group items by Supplier (Product.supplier is a User FK; map to Supplier)
    items_by_supplier_id = defaultdict(list)
    for item in cart.items.all():
        supplier = Supplier.objects.filter(user_id=item.product.supplier_id).first()
        if not supplier:
            return Response({'error': f'No Supplier profile for product {item.product.id}'}, status=status.HTTP_400_BAD_REQUEST)
        items_by_supplier_id[supplier.id].append(item)

    created_orders = []

    try:
        with transaction.atomic():
            for supp_id, items in items_by_supplier_id.items():
                supplier = Supplier.objects.select_for_update().get(id=supp_id)

                placed = Order.objects.create(
                    user_id=user.id,
                    supplier=supplier,
                    status='pending'
                )

                for item in items:
                    prod = item.product
                    if item.quantity > prod.quantity_available:
                        return Response({'error': f'Insufficient stock for {prod.name}'}, status=status.HTTP_400_BAD_REQUEST)

                    OrderItem.objects.create(
                        order=placed,
                        product=prod,
                        quantity=item.quantity,
                        price_at_order=Decimal(prod.price)
                    )

                    # Optional: decrement stock now or upon approval/completion
                    # prod.quantity_available -= item.quantity
                    # prod.save(update_fields=['quantity_available'])

                created_orders.append(placed)

            # Clear the cart items (keep the empty cart row)
            cart.items.all().delete()

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    data = OrderSerializer(created_orders, many=True).data
    return Response(data, status=status.HTTP_201_CREATED)