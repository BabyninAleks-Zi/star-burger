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
    products = OrderProductSerializer(many=True, allow_empty=False)

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        order = Order.objects.create(**validated_data)

        order_items = []
        for item in products_data:
            order_items.append(OrderItem(
                order=order,
                product_id=item['product'],
                quantity=item['quantity'],
            ))

        OrderItem.objects.bulk_create(order_items)
        return order
