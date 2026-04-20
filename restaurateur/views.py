from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from collections import defaultdict


from foodcartapp.models import Order, Product, Restaurant, RestaurantMenuItem


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item   in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = list(
        Order.objects
              .exclude(status=Order.Status.DELIVERED)
              .with_total_cost()
              .select_related('restaurant')
              .prefetch_related('items__product')
    )

    all_order_product_ids = {
        item.product_id
        for order in orders
        if order.restaurant_id is None
        for item in order.items.all()
    }

    restaurants_by_product = defaultdict(set)
    restaurant_names = {}
    menu_items = RestaurantMenuItem.objects.filter(
        availability=True,
        product_id__in=all_order_product_ids,
    ).values_list('product_id', 'restaurant_id', 'restaurant__name')

    for product_id, restaurant_id, restaurant_name in menu_items:
        restaurants_by_product[product_id].add(restaurant_id)
        restaurant_names[restaurant_id] = restaurant_name

    for order in orders:
        order.available_restaurants = []
        if order.restaurant_id:
            continue

        order_product_ids = [item.product_id for item in order.items.all()]
        if not order_product_ids:
            continue

        available_restaurant_ids = set(
            restaurants_by_product.get(order_product_ids[0], set())
        )
        for product_id in order_product_ids[1:]:
            available_restaurant_ids &= restaurants_by_product.get(product_id, set())

        order.available_restaurants = sorted(
            (
                {'id': restaurant_id, 'name': restaurant_names[restaurant_id]}
                for restaurant_id in available_restaurant_ids
            ),
            key=lambda restaurant: restaurant['name'],
        )

    return render(request, template_name='order_items.html', context={
        'order_items': orders,
    })
