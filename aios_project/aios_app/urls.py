from django.urls import path

from .api_views.orderView.order_view import create_order,get_order,list_orders,add_cart_item,checkout_cart,get_cart,remove_cart_item,update_cart_item
from .api_views.supplierView.supplier_views import list_suppliers,create_supplier,get_supplier
from .api_views.authentications import user_view
from .api_views.recommendationView import recommendation_view
from .api_views.recommendationView import input_usage_view
from .api_views.supplierView.product_views import create_product,product_detail,list_products,list_products_by_supplier
from .api_views.recommendationView.fertlizer_usageView import get_fertilizer_plan
urlpatterns = [
    path('register/', user_view.register_user, name='register'),
    path('login/', user_view.login, name='login'),
    path('users/', user_view.list_users, name='list_users'),
    path('users/<int:user_id>/', user_view.get_user_by_id, name='get_user_by_id'),
    path('recommendation/', recommendation_view.create_recommendation, name='create_recommendation'),
    path('recommendation/', recommendation_view.get_recommendations, name='get_recommendations'),
    path('prediction/', recommendation_view.create_prediction, name='create_prediction'),
    path('crop-prediction/', recommendation_view.create_crop_only_prediction, name='create_crop_only_prediction'),
    path('input-usage-prediction/', input_usage_view.predict_input_usage, name='input_usage_prediction'),
    path('suppliers/', list_suppliers, name='list_suppliers'),
    path('suppliers/create/', create_supplier, name='create_supplier'),
    path('suppliers/<int:supplier_id>/', get_supplier, name='get_supplier'),
    path('products/create/', create_product, name='create_product'),
    path('products/', list_products, name='list_products'),
    # path('products/<int:product_id>/', get_product, name='get_product'),
    path('products/<int:product_id>/', product_detail, name='product-detail'),
    path('products/supplier/<int:supplier_id>/', list_products_by_supplier, name='list_products_by_supplier'),
    path('fertilizer/<str:crop_name>/', get_fertilizer_plan, name='get_fertilizer_plan'),
    path('orders/create/', create_order, name='order-create'),
    path('orders/', list_orders, name='order-list'),
    path('orders/<int:order_id>/', get_order, name='order-detail'),
     path('orders/cart/', get_cart, name='cart-get'),
    path('orders/cart/items/', add_cart_item, name='cart-add-item'),
    path('orders/cart/items/<int:item_id>/', update_cart_item, name='cart-update-item'),
    path('orders/cart/items/<int:item_id>/remove/', remove_cart_item, name='cart-remove-item'),
    path('orders/cart/checkout/', checkout_cart, name='cart-checkout'),
]