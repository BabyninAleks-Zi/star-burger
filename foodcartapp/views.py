import json
from django.db import transaction
from django.http import JsonResponse
from django.templatetags.static import static


from .models import Order, OrderItem, Product


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def register_order(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)

    try:
        data_order = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    required_fields = ['firstname', 'lastname', 'phonenumber', 'address', 'products']
    missing_fields = [field for field in required_fields if not data_order.get(field)]
    if missing_fields:
        return JsonResponse({
            'error': 'Required fields are missing',
            'missing_fields': missing_fields,
        }, status=400)

    products_data = data_order['products']
    if not isinstance(products_data, list):
        return JsonResponse({'error': 'Products must be a list'}, status=400)

    product_ids = [item.get('product') for item in products_data]
    products = Product.objects.in_bulk(product_ids)

    order_items = []
    for item in products_data:
        product_id = item.get('product')
        quantity = item.get('quantity')

        if product_id not in products:
            return JsonResponse({'error': f'Product {product_id} does not exist'}, status=400)
        if not isinstance(quantity, int) or quantity < 1:
            return JsonResponse({
                'error': f'Invalid quantity for product {product_id}',
            }, status=400)

        order_items.append(OrderItem(
            product=products[product_id],
            quantity=quantity,
        ))

    order = Order(
        firstname=data_order['firstname'],
        lastname=data_order['lastname'],
        phonenumber=data_order['phonenumber'],
        address=data_order['address'],
    )

    try:
        order.full_clean()
        for order_item in order_items:
            order_item.full_clean(exclude=['order'])
    except Exception as error:
        return JsonResponse({'error': str(error)}, status=400)

    with transaction.atomic():
        order.save()
        for order_item in order_items:
            order_item.order = order
        OrderItem.objects.bulk_create(order_items)

    return JsonResponse({'status': 'ok', 'order_id': order.id})
