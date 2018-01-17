import os

from keras.callbacks import TensorBoard, ModelCheckpoint
from keras.preprocessing.image import ImageDataGenerator

from ml_common.ml_models import IMG_ROWS, IMG_COLS, BATCH_SIZE, inception_resnet_v2


def train_model(base_dir, num_classes, saved_model_path, steps_per_epoch, epochs):
    # model = resnet50_model(IMG_ROWS, IMG_COLS, MODEL_CHANNELS, num_classes)
    model = inception_resnet_v2(num_classes)

    tensorboard = TensorBoard(
        log_dir=os.path.join(base_dir, 'logs'),
        histogram_freq=0,
        batch_size=BATCH_SIZE,
        write_graph=True,
        write_grads=False,
        write_images=False,
        embeddings_freq=0,
        embeddings_layer_names=None,
        embeddings_metadata=None,
    )

    checkpoint = ModelCheckpoint(
        filepath=os.path.join(
            os.path.dirname(saved_model_path),
            'checkpoint-.{epoch:02d}-{val_loss:.2f}.h5'
        ),
        monitor='val_acc',
        verbose=1,
        save_best_only=True,
    )

    train_data = ImageDataGenerator(
        rotation_range=25,
        zoom_range=0.3,
        fill_mode='constant',
        cval=0,
        horizontal_flip=True,
        data_format='channels_last',
    ).flow_from_directory(
        os.path.join(base_dir, 'dataset', 'train'),
        target_size=(IMG_ROWS, IMG_COLS),
        batch_size=16,
    )

    validation_data = ImageDataGenerator(
        data_format='channels_last',
    ).flow_from_directory(
        os.path.join(base_dir, 'dataset', 'validation'),
        target_size=(IMG_ROWS, IMG_COLS),
        batch_size=16,
    )

    model.fit_generator(
        train_data,
        steps_per_epoch=steps_per_epoch,
        epochs=epochs,
        callbacks=[
            tensorboard,
            checkpoint,
        ],
        validation_data=validation_data,
        shuffle=True,
        verbose=1,
    )

    print('Saving model...')
    model.save(saved_model_path)
