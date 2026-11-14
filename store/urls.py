
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path(
        'product/<int:product_id>/',
        views.product_detail,
        name='product_detail'
    ),
    path(
        'product/<int:product_id>/review/',
        views.add_review,
        name='add_review'
    ),

    path(
        'wishlist/',
        views.wishlist,
        name='wishlist'
    ),
    path(
        'wishlist/toggle/<int:product_id>/',
        views.toggle_wishlist,
        name='toggle_wishlist'
    ),

    path(
        'add-to-cart/<int:product_id>/',
        views.add_to_cart,
        name='add_to_cart'
    ),
    path('cart/', views.cart, name='cart'),
    path(
        'remove-cart/<int:item_id>/',
        views.remove_from_cart,
        name='remove_from_cart'
    ),

    path('checkout/', views.checkout, name='checkout'),
    path(
        'order-success/<int:order_id>/',
        views.order_success,
        name='order_success'
    ),
    path('orders/', views.orders, name='orders'),
    path('profile/', views.profile, name='profile'),
]
