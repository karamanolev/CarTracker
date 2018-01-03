from rest_framework import serializers


class MobileBgAdUpdateSerializer(serializers.Serializer):
    date = serializers.DateTimeField()
    type = serializers.IntegerField()
    type_name = serializers.CharField(source='get_type_display')
    active = serializers.BooleanField()
    model_name = serializers.CharField()
    model_mod = serializers.CharField()
    price = serializers.IntegerField()
    price_currency = serializers.IntegerField()
    price_currency_name = serializers.CharField(source='get_price_currency_display')
    registration_date = serializers.DateField()
    engine_type = serializers.IntegerField()
    engine_type_name = serializers.CharField(source='get_engine_type_display')
    mileage_km = serializers.IntegerField()
    power_hp = serializers.IntegerField()


class MobileBgAdSerializer(serializers.Serializer):
    adv = serializers.CharField()
    active = serializers.BooleanField()
    updates = MobileBgAdUpdateSerializer(many=True)
