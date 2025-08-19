from django.urls import path

from .api_views.farmer.usageView import list_my_usages,create_usage,delete_usage,update_usage,get_usage,usage_summary,list_all_usages

from .api_views.farmer.farmerView import my_farmer_profile,create_my_farmer_profile,list_farmers,update_my_farmer_profile,get_farmer
from .api_views.orderView.order_view import create_order,get_order,list_orders,add_cart_item,checkout_cart,get_cart,remove_cart_item,update_cart_item,update_order_status
from .api_views.supplierView.supplier_views import list_suppliers,create_supplier,get_supplier,update_supplier,supplier_by_user
from .api_views.authentications import user_view
from .api_views.recommendationView import input_usage_view
from .api_views.supplierView.product_views import create_product,product_detail,list_products,list_products_by_supplier
from .api_views.recommendationView.fertlizer_usageView import get_fertilizer_plan,submit_fertilizer_to_agronomist
from .api_views.recommendationView.recommendation_view import (
    submit_recommendation, my_recommendations, agronomist_inbox,
    claim_recommendation, review_recommendation, get_recommendation,
    create_prediction, create_crop_only_prediction,my_reviews,all_recommendations_for_agronomist
)

urlpatterns = [
    path('register/', user_view.register_user, name='register'),
    path('login/', user_view.login, name='login'),
    path('users/', user_view.list_users, name='list_users'),
    path('users/<int:user_id>/', user_view.get_user_by_id, name='get_user_by_id'),
    path('fertilizer/submit/', submit_fertilizer_to_agronomist, name='fertilizer-submit'),
    path('fertilizer/<str:crop_name>/', get_fertilizer_plan, name='fertilizer-plan'),
    path('recommendations/agronomist-all/', all_recommendations_for_agronomist, name='all_recommendations_for_agronomist'),
    path('recommendations/submit/', submit_recommendation),
    path('recommendations/my/', my_recommendations),
    path('my-reviews/',my_reviews ),
    path('recommendations/inbox/', agronomist_inbox),
    path('recommendations/<int:rec_id>/', get_recommendation),
    path('recommendations/<int:rec_id>/claim/', claim_recommendation),
    path('recommendations/<int:rec_id>/review/', review_recommendation),    
    path('prediction/',create_prediction, name='create_prediction'),
    path('crop-prediction/', create_crop_only_prediction, name='create_crop_only_prediction'),
    path('input-usage-prediction/', input_usage_view.predict_input_usage, name='input_usage_prediction'),
    path('suppliers/', list_suppliers, name='list_suppliers'),
    path('suppliers/create/', create_supplier, name='create_supplier'),
    # path('suppliers/<int:user_id>/', get_supplier, name='get_supplier'),
    path('suppliers/<int:user_id>/', supplier_by_user, name='supplier-by-user'),
    path('products/create/', create_product, name='create_product'),
    path('products/', list_products, name='list_products'),
    # path('products/<int:product_id>/', get_product, name='get_product'),
    path('products/<int:product_id>/', product_detail, name='product-detail'),
    path('products/supplier/<int:supplier_id>/', list_products_by_supplier, name='list_products_by_supplier'),
    # path('fertilizer/<str:crop_name>/', get_fertilizer_plan, name='get_fertilizer_plan'),
    path('orders/create/', create_order, name='order-create'),
    path('orders/', list_orders, name='order-list'),
    path('orders/<int:order_id>/', get_order, name='order-detail'),
    path('orders/cart/', get_cart, name='cart-get'),
    path('orders/cart/items/', add_cart_item, name='cart-add-item'),
    path('orders/cart/items/<int:item_id>/', update_cart_item, name='cart-update-item'),
    path('orders/cart/items/<int:item_id>/remove/', remove_cart_item, name='cart-remove-item'),
    path('orders/cart/checkout/', checkout_cart, name='cart-checkout'),
    path('orders/<int:order_id>/status/', update_order_status, name='order-update-status'),


    path('farmers/me/', my_farmer_profile, name='farmer-me'),
    path('farmers/me/create/', create_my_farmer_profile, name='farmer-create-me'),
    path('farmers/me/update/', update_my_farmer_profile, name='farmer-update-me'),

    path('farmers/', list_farmers, name='farmers-list'),
    path('farmers/<int:farmer_id>/', get_farmer, name='farmer-detail'),
    path('usages/', list_my_usages, name='list-my-usages'),
    path('usages/create/', create_usage, name='create-usage'),
    path('usages/<int:usage_id>/', get_usage, name='get-usage'),
    path('usages/<int:usage_id>/update/', update_usage, name='update-usage'),
    path('usages/<int:usage_id>/delete/', delete_usage, name='delete-usage'),
    path('usages/summary/', usage_summary, name='usage-summary'),
    path('admin/usages/', list_all_usages, name='list-all-usages')
]