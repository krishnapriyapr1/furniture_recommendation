from django.shortcuts import render, redirect
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views
from .views import (
    chatbot_view, index, supplier_list, user_register, admin_login, user_login, admin_add,
    adminpage, edit_product, delete_product, add_to_cart, decrease_to_cart,
    cart, checkout_view, search_view, user_logout, admin_order_view,
    order_detail_view, user_order_view, product_detail, add_to_wishlist,
    remove_to_wishlist, remove_from_cart, view_to_wishlist, order_summary_view,
    profile_update, update_status, order_list_and_detail, supplier_login,
    supplier_index, updateStock, sendStockUpdateRequest, request_password_reset,
    reset_password, furniture_recommendation  # Added furniture_recommendation import
)

urlpatterns = [
    path('admin_login/', views.admin_login, name='admin_login'),
    path('search/', views.search_view, name='search'),
    path('user_login/', views.user_login, name='user_login'),
    path('user/register/', views.user_register, name='user_register'),
    path('user_logout/', views.user_logout, name='user_logout'),
    path('register/', user_register, name='user_register'),
    path('accounts/', include("django.contrib.auth.urls")),
    path('admin_add/', views.admin_add, name='admin_add'),
    path('adminpage/', views.adminpage, name='adminpage'),
    path('adminpageorder/', views.admin_order_view, name='adminorders'),
    path('adminordersiteam/<int:order_id>/', views.order_detail_view, name='order_detail'),
    path('userpageorder/', views.user_order_view, name='orders'),
    path('', views.index, name='index'),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('add_to_wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_to_wishlist/<int:product_id>/', views.remove_to_wishlist, name='remove_to_wishlist'),
    path('dec_from_cart/<int:product_id>/', views.decrease_to_cart, name='decrease_quantity'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.cart, name='cart'),
    path('view_to_wishlist/', views.view_to_wishlist, name='view_to_wishlist'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('order_summary/', views.order_summary_view, name='order_summary'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('update_status/<int:order_id>/', views.update_status, name='update_status'),
    path('order_list_and_detail/', views.order_list_and_detail, name='order_list_and_detail'),
    path('supplier/login/', views.supplier_login, name="supplier_login"),
    path('supplier/', views.supplier_index, name="supplier_dashboard"),
    path('updateStock/', views.updateStock, name='update_stock'),
    path('supplier/details/', views.supplier_list, name='suppliers'),
    path('sendStockUpdateRequest/<int:product_id>/', views.sendStockUpdateRequest, name='send_stock_update_request'),
    path('request_password_reset/', views.request_password_reset, name='request_password_reset'),
    path('change-password/<str:token>/<str:userid>/', views.reset_password, name='reset_password'),
    path('furniture_recommendation/', views.furniture_recommendation, name='furniture_recommendation'), 
    path('recommendation/', furniture_recommendation, name='furniture_recommendation'),
    path('visualization/', views.visualization_result, name='visualization_result'),
    path('recommendation-results/', views.recommendation_results, name='recommendation_results'),
    path('chatbot/', chatbot_view, name='chatbot'), 
     # Other paths
    path('download/csv/', views.download_csv, name='download_csv'),
    path('download/pdf/', views.download_pdf, name='download_pdf'),
]
    
     # Added URL path for furniture recommendation
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
