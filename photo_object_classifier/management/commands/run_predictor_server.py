import json
import traceback
from io import BytesIO

import numpy
from aiohttp import web
from django.core.management import BaseCommand
from keras.models import load_model

from photo_object_classifier.ml_models import CLASSES, set_tf_session, SAVED_MODEL_PATH, \
    load_img_from_buffer


class Command(BaseCommand):
    async def index(self, request):
        try:
            data = await request.read()

            d = load_img_from_buffer(BytesIO(data))
            d = numpy.expand_dims(d, axis=0)
            pred = self.model.predict(d, batch_size=16)[0]
            class_index = int(pred.argmax())
            class_name = CLASSES[class_index]

            return web.Response(text=json.dumps({
                'class_index': class_index,
                'class_name': class_name,
            }))
        except Exception:
            return web.Response(text=json.dumps({
                'error': traceback.format_exc(),
            }))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = None

    def handle(self, *args, **options):
        set_tf_session()
        self.model = load_model(SAVED_MODEL_PATH)

        app = web.Application()
        app.router.add_post('/', self.index)
        web.run_app(app, host='127.0.0.1', port=9090)
