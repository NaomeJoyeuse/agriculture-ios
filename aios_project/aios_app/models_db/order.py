from django.db import models
from django.db.models import Q, UniqueConstraint
from .user import User
from .supplier import Product  # you still need Product

class Order(models.Model):
    orderID = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')

    # Now points to User (the seller). Keep nullable for global cart.
    supplier = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders_as_supplier',
        null=True,
        blank=True,
        limit_choices_to={'role': 'supplier'},  # adjust to your role field/values
    )

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

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-orderDate']
        constraints = [
            UniqueConstraint(fields=['user'], condition=Q(status='cart'), name='uniq_active_cart_per_user'),
        ]

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.product.name} x {self.quantity} (Order {self.order.orderID})"