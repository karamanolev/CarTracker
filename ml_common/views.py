from base64 import b64encode

import requests
from django.shortcuts import render
from django.views import View

from mobile_bg.models import MobileBgAdImage


class DemoViewBase(View):
    def get_class_display(self, class_index):
        pass

    def dispatch(self, request, *args, **kwargs):
        url = ''
        image_data = None
        results = None
        if request.method == 'POST':
            url = request.POST.get('url')
            if url:
                image_data = requests.get(url).content
            file = request.FILES.get('file')
            if file:
                image_data = file.read()
            if image_data:
                results = self.get_class_display(image_data)
        return render(request, 'ml_common/demo.html', {
            'url': url,
            'class_names': results,
            'image_base64': b64encode(image_data or b'').decode(),
        })


class DemoView(DemoViewBase):
    def get_class_display(self, image_data):
        from photo_object_classifier.api import classify_blob_photo_object
        from photo_model_classifier.api import classify_blob_photo_model
        return [
            MobileBgAdImage.photo_object_to_str(classify_blob_photo_object(image_data)),
            classify_blob_photo_model(image_data),
        ]
