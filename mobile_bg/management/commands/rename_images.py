from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from mobile_bg.models import MobileBgAdImage, _image_small_upload_to, _image_big_upload_to


class Command(BaseCommand):
    def fix_images(self, ad_im):
        small_content = ad_im.image_small.read()
        big_content = ad_im.image_big.read()
        ad_im.image_small = ContentFile(small_content, '{}.jpg'.format(ad_im.index))
        ad_im.image_big = ContentFile(big_content, '{}.jpg'.format(ad_im.index))
        ad_im.save()

    def handle(self, *args, **options):
        print('Scanning...')
        for i, item in enumerate(MobileBgAdImage.objects.all()):
            original_filename = '{}.jpg'.format(item.index)
            small_path = _image_small_upload_to(item, original_filename)
            big_path = _image_big_upload_to(item, original_filename)

            if small_path != item.image_small.name or big_path != item.image_big.name:
                if small_path != item.image_small.name:
                    pass  # print('Fix {} -> {}'.format(item.image_small.name, small_path))
                if big_path != item.image_big.name:
                    pass  # print('Fix {} -> {}'.format(item.image_big.name, big_path))
                self.fix_images(item)

            if i % 50 == 0:
                print('{}'.format(i + 1))
