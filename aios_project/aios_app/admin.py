from django.contrib import admin

# Register your models here.
from .models_db.user import User
from .models_db.recommendation import CropRecommendation
from .models_db.supplier import Supplier, Product
from .models_db.order import Order
from .models_db.feedback import Feedback
from .models_db.input_usage import InputUsage

admin.site.register(User)
admin.site.register(CropRecommendation)
admin.site.register(Supplier)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Feedback)
admin.site.register(InputUsage)