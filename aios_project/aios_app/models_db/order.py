# from django.db import models
# from .user import User
# from .supplier import Supplier, Product

# class Order(models.Model):
#     orderID = models.AutoField(primary_key=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
#     supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='orders')
#     orderDate = models.DateTimeField(auto_now_add=True)
#     status = models.CharField(
#         max_length=30,
#         choices=[
#             ('pending', 'Pending'),
#             ('approved', 'Approved'),
#             ('rejected', 'Rejected'),
#             ('completed', 'Completed'),
#             ('cart', 'Cart'), 
#         ],
#         default='cart'
#     )

#     def __str__(self):
#         return f"Order {self.orderID} by {self.user.username}"

#     class Meta:
#         verbose_name = 'Order'
#         verbose_name_plural = 'Orders'
#         ordering = ['-orderDate']

# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField()
#     price_at_order = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Optional

#     def __str__(self):
#         return f"{self.product.name} x {self.quantity} (Order {self.order.orderID})"



from django.db import models
from django.db.models import Q, UniqueConstraint
from .user import User
from .supplier import Supplier, Product

class Order(models.Model):
    orderID = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')

    # allow NULL for global cart; non-null for placed orders
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)

    orderDate = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=30,
        choices=[
            ('cart', 'Cart'),
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('completed', 'Completed'),
        ],
        default='cart'
    )

    def __str__(self):
        return f"Order {self.orderID} by {self.user.username}"

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-orderDate']
        constraints = [
            # One active cart per user
            UniqueConstraint(fields=['user'], condition=Q(status='cart'), name='uniq_active_cart_per_user'),
        ]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.product.name} x {self.quantity} (Order {self.order.orderID})"