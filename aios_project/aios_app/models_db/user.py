# from django.db import models

# class User(models.Model):
#     ROLE_CHOICES = [
#         ('farmer', 'farmer'),
#         ('supplier', 'supplier'),
#         ('admin', 'admin'),
#         ('leader', 'leader'),
#         ('agronomist','agronomist')
#     ]
    
#     username = models.CharField(max_length=100, unique=True)
#     email = models.EmailField(unique=True)
#     password = models.CharField(max_length=255)
#     role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='farmer')
#     address = models.TextField(blank=True, null=True)
#     phone_number = models.CharField(max_length=15, blank=True, null=True)

#     def __str__(self):
#         return self.username


from django.db import models

class User(models.Model):
    ROLE_CHOICES = [
        ('farmer', 'farmer'),
        ('supplier', 'supplier'),
        ('admin', 'admin'),
        ('leader', 'leader'),
        ('agronomist','agronomist'),
    ]

    STATUS_CHOICES = [
        ('active', 'active'),
        ('inactive', 'inactive'),
        ('suspended', 'suspended'),
    ]

    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='farmer')
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    # New field
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', db_index=True)

    def __str__(self):
        return self.username

    # Helpers
    def activate(self, save=True):
        self.status = 'active'
        if save: self.save(update_fields=['status'])

    def deactivate(self, save=True):
        self.status = 'inactive'
        if save: self.save(update_fields=['status'])

    def suspend(self, save=True):
        self.status = 'suspended'
        if save: self.save(update_fields=['status'])