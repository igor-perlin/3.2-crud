from rest_framework import serializers
from logistic.models import Product, StockProduct, Stock

# исправлено 12/12/23

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description']

class ProductPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockProduct
        fields = ['id', 'product', 'quantity', 'price']

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
                    position_item, _ = StockProduct.objects.update_or_create(
                        id=position_id, stock=instance,
                        defaults={key: value for key, value in position_data.items() if key != 'id'}
                    )
                else:
                    StockProduct.objects.create(stock=instance, **position_data)
        return instance
