from django.db import transaction
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


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


@api_view(['GET', 'POST'])
def register_order(request):
    if request.method == 'GET':
        return Response({
            'detail': 'Отправьте POST с данными заказа в формате JSON.',
            'example': {
                'firstname': 'Иван',
                'lastname': 'Иванов',
                'phonenumber': '+79991234567',
                'address': 'Москва, ул. Пушкина, д. 1',
                'products': [
                    {'product': 1, 'quantity': 2}
                ]
            }
        })

    data_order = request.data

    required_fields = ['firstname', 'lastname', 'phonenumber', 'address', 'products']
    missing_fields = [field for field in required_fields if not data_order.get(field)]
    if missing_fields:
        return Response({
            'error': 'Required fields are missing',
            'missing_fields': missing_fields,
        }, status=status.HTTP_400_BAD_REQUEST)

    products_data = data_order['products']
    if not isinstance(products_data, list):
        return Response({'error': 'Products must be a list'}, status=status.HTTP_400_BAD_REQUEST)

    product_ids = [item.get('product') for item in products_data]
    products = Product.objects.in_bulk(product_ids)

    order_items = []
    for item in products_data:
        product_id = item.get('product')
        quantity = item.get('quantity')

        if product_id not in products:
            return Response(
                {'error': f'Product {product_id} does not exist'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not isinstance(quantity, int) or quantity < 1:
            return Response({
                'error': f'Invalid quantity for product {product_id}',
            }, status=status.HTTP_400_BAD_REQUEST)

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
        return Response({'error': str(error)}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        order.save()
        for order_item in order_items:
            order_item.order = order
        OrderItem.objects.bulk_create(order_items)

    return Response({'status': 'ok', 'order_id': order.id}, status=status.HTTP_201_CREATED)
