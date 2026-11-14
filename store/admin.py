
from django.contrib import admin
from .models import (
    Product,
    Cart,
    CartItem,
    Order,
    OrderItem,
    Review,
    WishlistItem,
)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'price',
        'available',
        'stock_quantity',
        'created_at',
    )
    list_filter = ('category', 'available')
    search_fields = ('name', 'description')
    list_editable = ('available', 'stock_quantity')


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user',)
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'order_date', 'status')
    list_filter = ('status', 'order_date')
    search_fields = ('user__username',)
    inlines = [OrderItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__username')


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    search_fields = ('user__username', 'product__name')
