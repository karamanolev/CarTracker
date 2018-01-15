import json
import traceback
from io import BytesIO

import numpy
from aiohttp import web
from django.conf import settings
from django.core.management import BaseCommand
from keras.models import load_model

from ml_common.ml_models import load_img_from_buffer, set_tf_session
from photo_object_classifier.ml_models import POC_CLASSES, POC_SAVED_MODEL_PATH


class Command(BaseCommand):
    async def index(self, request):
        try:
            data = await request.read()

            d = load_img_from_buffer(BytesIO(data))
            d = numpy.expand_dims(d, axis=0)
            pred = self.model.predict(d, batch_size=16)[0]
            class_index = int(pred.argmax())
            class_name = POC_CLASSES[class_index]

            return web.Response(text=json.dumps({
                'class_index': class_index,
                'class_name': class_name,
                'version': settings.PHOTO_OBJECT_MODEL_VERSION,
            }))
        except Exception:
            return web.Response(text=json.dumps({
                'error': traceback.format_exc(),
            }))

    async def version(self, request):
        return web.Response(text=json.dumps({
            'version': settings.PHOTO_OBJECT_MODEL_VERSION,
        }))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = None

    def handle(self, *args, **options):
        set_tf_session()
        self.model = load_model(POC_SAVED_MODEL_PATH)

        app = web.Application(
            client_max_size=64 * 1024 ** 2,  # 64MB
        )
        app.router.add_post('/predict', self.index)
        app.router.add_get('/version', self.version)
        web.run_app(app, host='127.0.0.1', port=9090)