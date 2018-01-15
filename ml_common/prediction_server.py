import json
import traceback
from io import BytesIO

import numpy
from aiohttp import web
from keras.models import load_model

from ml_common.ml_models import load_img_from_buffer, set_tf_session


class PredictionServer:
    def __init__(self, model_path, model_version, classes):
        set_tf_session()
        self.model = load_model(model_path)
        self.model_version = model_version
        self.classes = classes

    async def index(self, request):
        try:
            data = await request.read()

            d = load_img_from_buffer(BytesIO(data))
            d = numpy.expand_dims(d, axis=0)
            pred = self.model.predict(d, batch_size=16)[0]
            class_index = int(pred.argmax())
            class_name = self.classes[class_index]

            return web.Response(text=json.dumps({
                'class_index': class_index,
                'class_name': class_name,
                'version': self.model_version,
            }))
        except Exception:
            return web.Response(text=json.dumps({
                'error': traceback.format_exc(),
            }))

    async def version(self, request):
        return web.Response(text=json.dumps({
            'version': self.model_version,
        }))

    def serve(self, port):
        app = web.Application(
            client_max_size=64 * 1024 ** 2,  # 64MB
        )
        app.router.add_post('/predict', self.index)
        app.router.add_get('/version', self.version)
        web.run_app(app, host='127.0.0.1', port=port)
