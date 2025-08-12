from django.db import models

class User(models.Model):
    ROLE_CHOICES = [
        ('farmer', 'farmer'),
        ('supplier', 'supplier'),
        ('admin', 'admin'),
        ('leader', 'leader'),
        ('agronomist','agronomist')
    ]
    
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='farmer')
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.username
