# from rest_framework import serializers
# from ..models_db.order import Order, OrderItem

# class OrderItemSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = OrderItem
#         fields = ['id', 'order', 'product', 'quantity', 'price_at_order']
#         read_only_fields = ['id']

# class OrderSerializer(serializers.ModelSerializer):
#     items = OrderItemSerializer(many=True)

#     class Meta:
#         model = Order
#         fields = [
#             'orderID', 'user', 'supplier', 'orderDate', 'status', 'items'
#         ]
#         read_only_fields = ['orderID', 'orderDate']

#     def create(self, validated_data):
#         items_data = validated_data.pop('items')
#         order = Order.objects.create(**validated_data)
#         for item_data in items_data:
#             OrderItem.objects.create(order=order, **item_data)
#         return order

#     def update(self, instance, validated_data):
#         items_data = validated_data.pop('items', None)
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()
#         if items_data is not None:
#             instance.items.all().delete()
#             for item_data in items_data:
#                 OrderItem.objects.create(order=instance, **item_data)
#         return instance



from rest_framework import serializers
from ..models_db.order import Order, OrderItem
from ..models_db.supplier import Product
from ..models_db.user import User


class OrderItemSerializer(serializers.ModelSerializer):
    # Helpful read-only fields for responses
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_image = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = OrderItem
        # Exclude 'order' from write; we set it in OrderSerializer.create/update
        fields = ['id', 'product', 'product_name', 'product_image', 'quantity', 'price_at_order']
        # If price_at_order is set during checkout, keep it read-only.
        read_only_fields = ['id', 'price_at_order']

    def get_product_image(self, obj):
        request = self.context.get('request')
        image_field = getattr(obj.product, 'image', None)
        if image_field and getattr(image_field, 'url', None):
            url = image_field.url
            return request.build_absolute_uri(url) if request else url
        return None


class OrderSerializer(serializers.ModelSerializer):
    # Nested items for create/update + response
    items = OrderItemSerializer(many=True)

    # Nice read-only fields
    user_username = serializers.CharField(source='user.username', read_only=True)
    supplier_username = serializers.CharField(source='supplier.username', read_only=True)

    class Meta:
        model = Order
        fields = [
            'orderID',
            'user', 'user_username',
            'supplier', 'supplier_username',   # supplier is a User FK (seller)
            'orderDate',
            'status',
            'items',
        ]
        read_only_fields = ['orderID', 'orderDate', 'user_username', 'supplier_username']

    def _validate_supplier_role(self, supplier: User):
        # Only validate if your User model has a role field
        role = getattr(supplier, 'role', None)
        if role is not None and str(role).lower() not in ('supplier', 'seller'):
            raise serializers.ValidationError({'supplier': 'Selected user is not a supplier'})

    def _enforce_products_belong_to_supplier(self, supplier_user_id: int, items_data):
        # items_data contains deserialized product instances (DRF resolves FK)
        for item in items_data:
            product = item.get('product')
            if not isinstance(product, Product):
                # If a raw id slipped through, fetch it
                product = Product.objects.get(pk=product)
            if product.supplier_id != supplier_user_id:
                raise serializers.ValidationError(
                    {'items': f'Product {product.id} does not belong to supplier user {supplier_user_id}'}
                )

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        supplier_user = validated_data.get('supplier', None)  # FK(User) or None (for carts if you use this path)

        # Validate supplier user role if supplied
        if isinstance(supplier_user, User):
            self._validate_supplier_role(supplier_user)

        order = Order.objects.create(**validated_data)

        # If a supplier user is set on the order, ensure all items’ products belong to that supplier user
        if order.supplier_id:
            self._enforce_products_belong_to_supplier(order.supplier_id, items_data)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)

        # Handle supplier change with role validation
        new_supplier = validated_data.get('supplier', serializers.empty)
        if new_supplier is not serializers.empty and isinstance(new_supplier, User):
            self._validate_supplier_role(new_supplier)

        # Update scalar fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Replace items if provided
        if items_data is not None:
            if instance.supplier_id:
                self._enforce_products_belong_to_supplier(instance.supplier_id, items_data)

            instance.items.all().delete()
            for item_data in items_data:
                OrderItem.objects.create(order=instance, **item_data)

        return instance