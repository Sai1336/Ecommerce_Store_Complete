import random
from django.views.decorators.http import require_http_methods
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Avg
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Cart

from .models import (
    Product,
    Cart,
    CartItem,
    Order,
    OrderItem,
    Review,
    WishlistItem,
)


def home(request):
    products = Product.objects.all().order_by('-created_at')
    category = request.GET.get('category', '').strip()
    search = request.GET.get('q', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()

    if category and category in dict(Product.CATEGORY_CHOICES):
        products = products.filter(category=category)

    if search:
        products = products.filter(name__icontains=search)

    try:
        if min_price:
            value = Decimal(min_price)
            if value >= 0:
                products = products.filter(price__gte=value)
            else:
                messages.error(request, 'Minimum price cannot be negative.')
    except (InvalidOperation, ValueError):
        messages.error(request, 'Enter a valid minimum price.')

    try:
        if max_price:
            value = Decimal(max_price)
            if value >= 0:
                products = products.filter(price__lte=value)
            else:
                messages.error(request, 'Maximum price cannot be negative.')
    except (InvalidOperation, ValueError):
        messages.error(request, 'Enter a valid maximum price.')

    return render(request, 'store/home.html', {
        'products': products,
        'categories': Product.CATEGORY_CHOICES,
        'selected_category': category,
        'search_query': search,
        'min_price': min_price,
        'max_price': max_price,
    })


def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'GET' or 'register_captcha_a' not in request.session:
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        request.session['register_captcha_a'] = a
        request.session['register_captcha_b'] = b

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        captcha_answer = request.POST.get('captcha_answer', '').strip()

        a = request.session.get('register_captcha_a')
        b = request.session.get('register_captcha_b')

        if a is None or b is None:
            messages.error(request, 'Please try the CAPTCHA again.')
            return redirect('register')

        if not captcha_answer.isdigit() or int(captcha_answer) != a + b:
            messages.error(request, 'Incorrect CAPTCHA answer. Please try again.')

            a = random.randint(1, 10)
            b = random.randint(1, 10)
            request.session['register_captcha_a'] = a
            request.session['register_captcha_b'] = b

            return render(request, 'store/register.html', {
                'captcha_a': a,
                'captcha_b': b,
            })

        request.session.pop('register_captcha_a', None)
        request.session.pop('register_captcha_b', None)

        if not username or not email or not password or not confirm_password:
            messages.error(request, 'Please fill in all fields.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'That username already exists.')
        elif password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        elif len(password) < 8:
            messages.error(request, 'Password must contain at least 8 characters.')
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            Cart.objects.create(user=user)
            messages.success(request, 'Account created. Please log in.')
            return redirect('login')

        # Generate a new CAPTCHA after a registration validation error.
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        request.session['register_captcha_a'] = a
        request.session['register_captcha_b'] = b

    return render(request, 'store/register.html', {
        'captcha_a': request.session['register_captcha_a'],
        'captcha_b': request.session['register_captcha_b'],
    })


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    # Generate a fresh question when opening the login page.
    if request.method == 'GET' or 'captcha_a' not in request.session:
        a = random.randint(1, 10)
        b = random.randint(1, 10)

        request.session['captcha_a'] = a
        request.session['captcha_b'] = b

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        captcha_answer = request.POST.get('captcha_answer', '').strip()

        a = request.session.get('captcha_a')
        b = request.session.get('captcha_b')

        if a is None or b is None:
            messages.error(request, 'Please try the CAPTCHA again.')
            return redirect('login')

        if not captcha_answer.isdigit() or int(captcha_answer) != a + b:
            messages.error(request, 'Incorrect CAPTCHA answer. Please try again.')

            # Generate a new question after a wrong answer.
            a = random.randint(1, 10)
            b = random.randint(1, 10)
            request.session['captcha_a'] = a
            request.session['captcha_b'] = b

            return render(request, 'store/login.html', {
                'captcha_a': a,
                'captcha_b': b,
            })

        # Consume the CAPTCHA so the same answer cannot be reused.
        request.session.pop('captcha_a', None)
        request.session.pop('captcha_b', None)

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            login(request, user)
            return redirect('home')

        messages.error(request, 'Invalid username or password.')

        # Generate a new CAPTCHA after failed login credentials.
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        request.session['captcha_a'] = a
        request.session['captcha_b'] = b

        return render(request, 'store/login.html', {
            'captcha_a': a,
            'captcha_b': b,
        })

    return render(request, 'store/login.html', {
        'captcha_a': request.session['captcha_a'],
        'captcha_b': request.session['captcha_b'],
    })


@require_POST
def logout_view(request):
    logout(request)
    return redirect('home')


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    reviews = product.reviews.select_related('user').all()
    average_rating = reviews.aggregate(
        average=Avg('rating')
    )['average']

    customer_review = None
    in_wishlist = False

    if request.user.is_authenticated:
        customer_review = Review.objects.filter(
            product=product,
            user=request.user
        ).first()

        in_wishlist = WishlistItem.objects.filter(
            product=product,
            user=request.user
        ).exists()

    return render(request, 'store/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'average_rating': average_rating,
        'review_count': reviews.count(),
        'customer_review': customer_review,
        'in_wishlist': in_wishlist,
    })


@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if not product.available:
        messages.error(request, 'This product is currently unavailable.')
        return redirect('product_detail', product_id=product.id)

    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        item.quantity += 1
        item.save()

    messages.success(request, 'Product added to your cart.')
    return redirect('cart')


@login_required
def cart(request):
    user_cart, _ = Cart.objects.get_or_create(user=request.user)
    items = user_cart.items.select_related('product')
    total = sum(
        (item.total_price() for item in items),
        Decimal('0.00')
    )

    return render(request, 'store/cart.html', {
        'items': items,
        'total': total,
    })


@login_required
@require_POST
def remove_from_cart(request, item_id):
    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )
    item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('cart')


@login_required
def checkout(request):
    user_cart, _ = Cart.objects.get_or_create(user=request.user)
    items = list(user_cart.items.select_related('product'))

    if not items:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')

    if request.method == 'POST':
        if any(not item.product.available for item in items):
            messages.error(
                request,
                'A product in your cart is unavailable. '
                'Please remove it before checkout.'
            )
            return redirect('cart')

        total = sum(
            (item.total_price() for item in items),
            Decimal('0.00')
        )

        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                total_amount=total
            )

            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )

            user_cart.items.all().delete()

        return redirect('order_success', order_id=order.id)

    total = sum(
        (item.total_price() for item in items),
        Decimal('0.00')
    )

    return render(request, 'store/checkout.html', {
        'items': items,
        'total': total,
    })


@login_required
def order_success(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )
    return render(request, 'store/order_success.html', {
        'order': order,
    })


@login_required
def orders(request):
    user_orders = (
        Order.objects.filter(user=request.user)
        .prefetch_related('items__product')
        .order_by('-order_date')
    )

    return render(request, 'store/orders.html', {
        'orders': user_orders,
    })


@login_required
def profile(request):
    return render(request, 'store/profile.html')


@login_required
def wishlist(request):
    items = WishlistItem.objects.filter(
        user=request.user
    ).select_related('product')

    return render(request, 'store/wishlist.html', {
        'items': items,
    })


@login_required
@require_POST
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    item = WishlistItem.objects.filter(
        user=request.user,
        product=product
    )

    if item.exists():
        item.delete()
        messages.success(request, 'Product removed from your wishlist.')
    else:
        WishlistItem.objects.create(
            user=request.user,
            product=product
        )
        messages.success(request, 'Product added to your wishlist.')

    return redirect('product_detail', product_id=product.id)


@login_required
@require_POST
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    rating_text = request.POST.get('rating', '')
    comment = request.POST.get('comment', '').strip()

    try:
        rating = int(rating_text)
    except (ValueError, TypeError):
        messages.error(request, 'Please select a valid star rating.')
        return redirect('product_detail', product_id=product.id)

    if rating < 1 or rating > 5:
        messages.error(request, 'Rating must be between 1 and 5.')
        return redirect('product_detail', product_id=product.id)

    if not comment:
        messages.error(request, 'Please write a review.')
        return redirect('product_detail', product_id=product.id)

    review, created = Review.objects.update_or_create(
        product=product,
        user=request.user,
        defaults={
            'rating': rating,
            'comment': comment,
        }
    )

    if created:
        messages.success(request, 'Thank you for your review!')
    else:
        messages.success(request, 'Your review has been updated.')

    return redirect('product_detail', product_id=product.id)
