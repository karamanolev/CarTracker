import os
from shutil import rmtree

from django.core.management.base import BaseCommand
from pip._vendor.distlib._backport import shutil

from mobile_bg.models import MobileBgAdImage


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('target_directory')

    def _copy_images(self, target, images):
        os.makedirs(target)
        written = 0
        for i, image in enumerate(images, 1):
            shutil.copyfile(
                image.image_big.path,
                os.path.join(target, '{}.jpg'.format(i)),
            )
            written += 1
        return written

    def _export_class(self, target, photo_object, class_name):
        print('Exporting {}'.format(class_name))
        images = list(MobileBgAdImage.objects.filter(photo_object=photo_object).order_by('id'))
        num_train = int(len(images) * 0.8)
        train = self._copy_images(os.path.join(target, 'train', class_name), images[:num_train])
        val = self._copy_images(os.path.join(target, 'validation', class_name), images[num_train:])
        print('Wrote {} training and {} validation samples'.format(train, val))

    def handle(self, *args, **options):
        target = os.path.abspath(options['target_directory'])
        target_contents = os.listdir(target)
        if target_contents:
            answer = input('Empty target? [y/n]: ')
            if answer == 'y':
                for i in target_contents:
                    print('Deleting', i)
                    rmtree(os.path.join(target, i))
            else:
                exit(1)
        self._export_class(target, MobileBgAdImage.PHOTO_OBJECT_EXTERIOR, 'exterior')
        self._export_class(target, MobileBgAdImage.PHOTO_OBJECT_INTERIOR, 'interior')
        self._export_class(target, MobileBgAdImage.PHOTO_OBJECT_ENGINE, 'engine')
        self._export_class(target, MobileBgAdImage.PHOTO_OBJECT_OTHER, 'other')
