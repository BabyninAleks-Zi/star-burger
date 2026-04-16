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
    errors = {}

    for field in ['firstname', 'lastname', 'phonenumber', 'address']:
        if field not in data_order:
            errors[field] = ['Обязательное поле.']
            continue

        value = data_order[field]

        if not isinstance(value, str):
            errors[field] = ['Недопустимая строка']
            continue

        if not value.strip():
            errors[field] = ['Это поле не может быть пустым.']

    products_data = data_order.get('products')

    if 'products' not in data_order:
        errors['products'] = ['Обязательное поле.']
    elif not isinstance(products_data, list):
        errors['products'] = ['Ожидался список товаров.']
    elif not products_data:
        errors['products'] = ['Список товаров не должен быть пустым.']

    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    for index, item in enumerate(products_data):
        if not isinstance(item, dict):
            return Response(
                {'products': [f'Элемент с индексом {index} должен быть объектом.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        if 'product' not in item:
            return Response(
                {'products': [f'У элемента с индексом {index} отсутствует поле product.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        if 'quantity' not in item:
            return Response(
                {'products': [f'У элемента с индексом {index} отсутствует поле quantity.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(item['product'], int):
            return Response(
                {'products': [f'Поле product в элементе {index} должно быть целым числом.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not isinstance(item['quantity'], int):
            return Response(
                {'products': [f'Поле quantity в элементе {index} должно быть целым числом.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        if item['quantity'] < 1:
            return Response(
                {'products': [f'Количество товара в элементе {index} должно быть больше 0.']},
                status=status.HTTP_400_BAD_REQUEST
            )

    product_ids = [item['product'] for item in products_data]
    products = Product.objects.in_bulk(product_ids)

    order_items = []
    for index, item in enumerate(products_data):
        product_id = item['product']
        quantity = item['quantity']

        if product_id not in products:
            return Response(
                {'products': [f'Продукт с id={product_id} не существует.']},
                status=status.HTTP_400_BAD_REQUEST
            )

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
