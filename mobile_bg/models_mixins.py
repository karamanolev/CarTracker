from django.db import models


class ColorMixin(models.Model):
    COLORS = [
        'Tъмно син',
        'Банан',
        'Беата',
        'Бежов',
        'Бордо',
        'Бронз',
        'Бял',
        'Винен',
        'Виолетов',
        'Вишнев',
        'Графит',
        'Жълт',
        'Зелен',
        'Златист',
        'Кафяв',
        'Керемиден',
        'Кремав',
        'Лилав',
        'Металик',
        'Оранжев',
        'Охра',
        'Пепеляв',
        'Перла',
        'Пясъчен',
        'Резидав',
        'Розов',
        'Сахара',
        'Светло сив',
        'Светло син',
        'Сив',
        'Син',
        'Слонова кост',
        'Сребърен',
        'Т.зелен',
        'Тъмно сив',
        'Тъмно син мет.',
        'Тъмно червен',
        'Тютюн',
        'Хамелеон',
        'Червен',
        'Черен'
    ]

    color = models.IntegerField(null=True, blank=True)

    @classmethod
    def color_to_code(cls, color_name):
        return cls.COLORS.index(color_name)

    @classmethod
    def code_to_color(cls, color_code):
        return cls.COLORS[color_code]

    class Meta:
        abstract = True


class VehicleTypeMixin(models.Model):
    VEHICLE_TYPE_CAR = 1
    VEHICLE_TYPE_SUV = 2
    VEHICLE_TYPE_VAN = 3
    VEHICLE_TYPE_TRUCK = 4
    VEHICLE_TYPE_MOTORCYCLE = 5
    VEHICLE_TYPE_AGRICULTURAL = 6
    VEHICLE_TYPE_INDUSTRIAL = 7
    VEHICLE_TYPE_MOTORCAR = 8
    VEHICLE_TYPE_CARAVAN = 9
    VEHICLE_TYPE_BOAT = ord('a')
    VEHICLE_TYPE_TRAILER = ord('b')
    VEHICLE_TYPE_BIKE = ord('c')
    VEHICLE_TYPE_PARTS = ord('u')
    VEHICLE_TYPE_ACCESSORIES = ord('v')
    VEHICLE_TYPE_TYRES_AND_RIMS = ord('w')
    VEHICLE_TYPE_BUYING = ord('y')
    VEHICLE_TYPE_SERVICES = ord('z')

    VEHICLE_TYPE_CHOICES = (
        (VEHICLE_TYPE_CAR, 'Кола'),
        (VEHICLE_TYPE_SUV, 'Джип'),
        (VEHICLE_TYPE_VAN, 'Бус'),
        (VEHICLE_TYPE_TRUCK, 'Камион'),
        (VEHICLE_TYPE_MOTORCYCLE, 'Мотоциклет'),
        (VEHICLE_TYPE_AGRICULTURAL, 'Селскостопански'),
        (VEHICLE_TYPE_INDUSTRIAL, 'Индустриален'),
        (VEHICLE_TYPE_MOTORCAR, 'Кар'),
        (VEHICLE_TYPE_CARAVAN, 'Каравана'),
    )

    VEHICLE_TYPE_BY_MOBILE_BG_NAME = {
        'Автомобили': VEHICLE_TYPE_CAR,
        'Джипове': VEHICLE_TYPE_SUV,
        'Бусове': VEHICLE_TYPE_VAN,
        'Камиони': VEHICLE_TYPE_TRUCK,
        'Мотоциклети': VEHICLE_TYPE_MOTORCYCLE,
    }

    vehicle_type = models.IntegerField(choices=VEHICLE_TYPE_CHOICES)

    @classmethod
    def get_mobile_bg_name_by_vehicle_type(cls, vehicle_type):
        for k, v in cls.VEHICLE_TYPE_BY_MOBILE_BG_NAME.items():
            if v == vehicle_type:
                return k
        raise Exception('Vehicle type not found')

    class Meta:
        abstract = True


class BodyStyleMixin(models.Model):
    BODY_STYLE_CAR_VAN = 101
    BODY_STYLE_CAR_CABRIOLET = 102
    BODY_STYLE_CAR_WAGON = 103
    BODY_STYLE_CAR_COUPE = 104
    BODY_STYLE_CAR_MINIVAN = 105
    BODY_STYLE_CAR_PICKUP = 106
    BODY_STYLE_CAR_SEDAN = 107
    BODY_STYLE_CAR_STRETCH_LIMO = 108
    BODY_STYLE_CAR_HATCHBACK = 109
    BODY_STYLE_CAR_CHOICES = (
        (BODY_STYLE_CAR_VAN, 'Ван'),
        (BODY_STYLE_CAR_CABRIOLET, 'Кабрио'),
        (BODY_STYLE_CAR_WAGON, 'Комби'),
        (BODY_STYLE_CAR_COUPE, 'Купе'),
        (BODY_STYLE_CAR_MINIVAN, 'Миниван'),
        (BODY_STYLE_CAR_PICKUP, 'Пикап'),
        (BODY_STYLE_CAR_SEDAN, 'Седан'),
        (BODY_STYLE_CAR_STRETCH_LIMO, 'Стреч лимузина'),
        (BODY_STYLE_CAR_HATCHBACK, 'Хечбек'),
    )

    BODY_STYLE_SUV_SHORT_WHEEL_BASE = 201
    BODY_STYLE_SUV_LONG_WHEEL_BASE = 202
    BODY_STYLE_SUV_PICKUP_SHORT_WHEEL_BASE = 203
    BODY_STYLE_SUV_PICKUP_LONG_WHEEL_BASE = 204
    BODY_STYLE_SUV_CHOICES = (
        (BODY_STYLE_SUV_SHORT_WHEEL_BASE, 'Къса база'),
        (BODY_STYLE_SUV_LONG_WHEEL_BASE, 'Дълга база'),
        (BODY_STYLE_SUV_PICKUP_SHORT_WHEEL_BASE, 'Пикап - Къса база'),
        (BODY_STYLE_SUV_PICKUP_LONG_WHEEL_BASE, 'Пикап - Дълга база'),
    )

    BODY_STYLE_CHOICES_BY_VEHICLE_TYPE = {
        VehicleTypeMixin.VEHICLE_TYPE_CAR: BODY_STYLE_CAR_CHOICES,
        VehicleTypeMixin.VEHICLE_TYPE_SUV: BODY_STYLE_SUV_CHOICES,
    }

    BODY_STYLE_CHOICES = sum(BODY_STYLE_CHOICES_BY_VEHICLE_TYPE.values(), ())

    body_style = models.IntegerField(null=True, blank=True, choices=BODY_STYLE_CHOICES)

    def get_body_style_by_mobile_bg_name(self, name):
        for k, v in self.BODY_STYLE_CHOICES_BY_VEHICLE_TYPE[self.ad.vehicle_type]:
            if v == name:
                return k
        raise Exception('Unknown body style name {}'.format(name))

    class Meta:
        abstract = True


class EngineTypeMixin(models.Model):
    ENGINE_PETROL = 0
    ENGINE_DIESEL = 1
    ENGINE_HYBRID = 2
    ENGINE_ELECTRIC = 3
    ENGINE_CHOICES = (
        (ENGINE_PETROL, 'Petrol'),
        (ENGINE_DIESEL, 'Diesel'),
        (ENGINE_HYBRID, 'Hybrid'),
        (ENGINE_ELECTRIC, 'Electric'),
    )

    engine_type = models.IntegerField(null=True, blank=True, choices=ENGINE_CHOICES)

    class Meta:
        abstract = True


class TransmissionTypeMixin(models.Model):
    TRANSMISSION_MANUAL = 0
    TRANSMISSION_AUTOMATIC = 1
    TRANSMISSION_SEMIAUTOMATIC = 2
    TRANSMISSION_CHOICES = (
        (TRANSMISSION_MANUAL, 'Manual'),
        (TRANSMISSION_AUTOMATIC, 'Automatic'),
        (TRANSMISSION_SEMIAUTOMATIC, 'Semiautomatic'),
    )

    transmission_type = models.IntegerField(null=True, blank=True, choices=TRANSMISSION_CHOICES)

    class Meta:
        abstract = True


class PriceMixin(models.Model):
    CURRENCY_BGN = 0
    CURRENCY_EUR = 1
    CURRENCY_USD = 2
    CURRENCY_CHOICES = (
        (CURRENCY_BGN, 'BGN'),
        (CURRENCY_EUR, 'EUR'),
        (CURRENCY_USD, 'USD'),
    )

    price = models.IntegerField(null=True, blank=True)
    price_currency = models.IntegerField(null=True, blank=True, choices=CURRENCY_CHOICES)

    class Meta:
        abstract = True
