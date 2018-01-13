import os

import tensorflow as tf
from django.conf import settings
from django.core.management.base import BaseCommand
from keras.backend import set_session
from keras.callbacks import TensorBoard
from keras.preprocessing.image import ImageDataGenerator

from photo_object_classifier.ml_models import resnet50_model, IMG_ROWS, IMG_COLS, MODEL_CHANNELS, \
    NUM_CLASSES, BATCH_SIZE

POC_BASE_DIR = os.path.join(settings.BASE_DIR, 'photo_object_classifier')


class Command(BaseCommand):
    def handle(self, *args, **options):
        config = tf.ConfigProto()
        config.gpu_options.per_process_gpu_memory_fraction = 0.9
        set_session(tf.Session(config=config))

        model = resnet50_model(IMG_ROWS, IMG_COLS, MODEL_CHANNELS, NUM_CLASSES)

        tb = TensorBoard(
            log_dir=os.path.join(POC_BASE_DIR, 'logs'),
            histogram_freq=0,
            batch_size=BATCH_SIZE,
            write_graph=True,
            write_grads=False,
            write_images=False,
            embeddings_freq=0,
            embeddings_layer_names=None,
            embeddings_metadata=None,
        )

        train_data = ImageDataGenerator(
            rotation_range=10,
            zoom_range=0.2,
            fill_mode='wrap',
            data_format='channels_last',
        ).flow_from_directory(
            os.path.join(POC_BASE_DIR, 'dataset', 'train'),
            target_size=(IMG_ROWS, IMG_COLS),
            batch_size=16,
        )

        validation_data = ImageDataGenerator(
            data_format='channels_last',
        ).flow_from_directory(
            os.path.join(POC_BASE_DIR, 'dataset', 'validation'),
            target_size=(IMG_ROWS, IMG_COLS),
            batch_size=16,
        )

        model.fit_generator(
            train_data,
            steps_per_epoch=512,
            epochs=10,
            callbacks=[tb],
            validation_data=validation_data,
            shuffle=True,
            verbose=1,
        )

        model.save(os.path.join(POC_BASE_DIR, 'saved_model.h5'))
