from django.db import transaction
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from .models import Order, OrderItem, Product


class OrderProductSerializer(serializers.Serializer):
    product = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_product(self, value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError(f'Продукт с id {value} не существует')
        return value


class OrderSerializer(serializers.Serializer):
    firstname = serializers.CharField()
    lastname = serializers.CharField()
    phonenumber = PhoneNumberField()
    address = serializers.CharField()
    products = OrderProductSerializer(many=True, write_only=True, allow_empty=False)

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        product_ids = [item['product'] for item in products_data]
        products = Product.objects.in_bulk(product_ids)
        with transaction.atomic():
            order = Order.objects.create(**validated_data)

            order_items = []
            for item in products_data:
                product = products[item['product']]
                order_items.append(OrderItem(
                    order=order,
                    product_id=item['product'],
                    quantity=item['quantity'],
                    price=product.price,
                ))

            OrderItem.objects.bulk_create(order_items)
        return order
