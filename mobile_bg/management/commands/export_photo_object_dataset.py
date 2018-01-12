import os
from shutil import rmtree

from django.core.management.base import BaseCommand
from pip._vendor.distlib._backport import shutil

from mobile_bg.models import MobileBgAdImage


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('target_directory')

    def _export_class(self, target, photo_object, class_name):
        class_target = os.path.join(target, class_name)
        os.makedirs(class_target)
        for i, image in enumerate(MobileBgAdImage.objects.filter(photo_object=photo_object), 1):
            shutil.copyfile(image.image_big.path, os.path.join(class_target, '{}.jpg'.format(i)))

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
