from ml_common.views import DemoViewBase
from photo_model_classifier.api import classify_blob_photo_model


class DemoView(DemoViewBase):
    def get_class_display(self, image_data):
        return [classify_blob_photo_model(image_data)]
