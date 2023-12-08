from rest_framework import serializers
from logistic.models import Product
from logistic.models import StockProduct
from .models import Stock



class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description']


class ProductPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockProduct
        fields = ['id', 'product', 'quantity', 'price']

    def validate(self, attrs):
        attrs.pop('stock', None)
        return super().validate(attrs)


class StockSerializer(serializers.ModelSerializer):
    positions = ProductPositionSerializer(many=True)

    class Meta:
        model = Stock
        fields = ['id', 'address', 'positions']

    def create(self, validated_data):
        positions_data = validated_data.pop('positions')
        stock = Stock.objects.create(**validated_data)
        for position_data in positions_data:
            StockProduct.objects.create(stock=stock, **position_data)
        return stock

    def update(self, instance, validated_data):
        positions_data = validated_data.pop('positions', None)
        instance = super().update(instance, validated_data)
        if positions_data is not None:
            for position_data in positions_data:
                position_id = position_data.get('id', None)
                if position_id:
                    position_item = StockProduct.objects.get(id=position_id, stock=instance)
                    for field, value in position_data.items():
                        setattr(position_item, field, value)
                    position_item.save()
                else:
                    StockProduct.objects.create(stock=instance, **position_data)
        return instance
