import requests


class SkipClassification(Exception):
    pass


class ClassificationError(Exception):
    pass


def classify_blob(model_version, port, blob):
    resp = requests.post('http://localhost:{}/predict'.format(port), data=blob)
    resp.raise_for_status()
    resp_data = resp.json()
    if 'error' in resp_data:
        raise Exception('Server returned {}'.format(resp.text))
    if resp_data['version'] != model_version:
        raise Exception('Incosistent codebase and server versions')
    return resp_data['class_name']


def classify_image(model_version, port, image):
    if image.photo_object_pred_v == model_version:
        raise SkipClassification('Already classified image {}.'.format(image.id))
    if not image.image_big:
        raise SkipClassification('No image_big for image {}'.format(image.id))
    data = image.image_big.read()
    if len(data) == 0:
        raise ClassificationError('Data is empty for image {}'.format(image.id))
    return classify_blob(model_version, port, data)
