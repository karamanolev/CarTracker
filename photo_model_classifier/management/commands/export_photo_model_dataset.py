import os
from shutil import rmtree

from django.core.management.base import BaseCommand
from pip._vendor.distlib._backport import shutil

from mobile_bg.models import MobileBgAdImage
from photo_model_classifier.ml_models import BRAND_TO_SLUG


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('num_samples', type=int)
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

    def _export_class(self, target, brand, class_name):
        print('Exporting {}'.format(class_name))
        images = list(MobileBgAdImage.objects.filter(
            photo_object_pred=MobileBgAdImage.PHOTO_OBJECT_EXTERIOR,
            ad__last_active_update__make_brand=brand,
        ).order_by('id')[:self.num_samples])
        num_train = int(len(images) * 0.8)
        train = self._copy_images(os.path.join(target, 'train', class_name), images[:num_train])
        val = self._copy_images(os.path.join(target, 'validation', class_name), images[num_train:])
        print('Wrote {} training and {} validation samples'.format(train, val))

    def handle(self, *args, **options):
        self.num_samples = options['num_samples']
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
        for brand, slug in BRAND_TO_SLUG.items():
            self._export_class(target, brand, slug)
