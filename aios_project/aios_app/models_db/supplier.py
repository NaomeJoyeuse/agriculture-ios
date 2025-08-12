from django.db import models
from .user import User  # Link to the User table for the Supplier model
from django.core.validators import FileExtensionValidator
# Supplier Table
class Supplier(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    contact_info = models.TextField()  # Can include phone number, email, etc.
    location = models.CharField(max_length=200)  # Address or service area
    status = models.CharField(max_length=50, default='Active')  # Active or Inactive

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'


# Product Table
class Product(models.Model):
    
    supplier = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)  # Product name (e.g., Urea)
    category = models.CharField(max_length=50)
    description =models.CharField(max_length=150)  # Category like fertilizer, pesticide, etc.
    quantity_available = models.IntegerField()  # Amount of stock available
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price per unit
    unit = models.CharField(max_length=20)  
    status = models.CharField(max_length=50, default='Available')  # Available or Unavailable
    image = models.ImageField(
        upload_to='products/images/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
    )

    def __str__(self):
        return f"{self.name} ({self.category})"

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
