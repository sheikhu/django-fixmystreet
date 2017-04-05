from django.core.management.base import BaseCommand, CommandError
from apps.fixmystreet.models import ReportFile
import Image
import ImageOps

class Command(BaseCommand):
    help = 'Resize existing thumbnail files to 140*140'

    def handle(self, *args, **options):
        files = ReportFile.objects.all()
        i = 0
        for file in files:
            if file.file_type == ReportFile.IMAGE:
                try:
                    original_width = file.image.width
                    original_height = file.image.height

                    if original_height > original_width:
                        ratio = 140/float(original_height)
                    else:
                         ratio = 140/float(original_width)


                    width = int(round(original_width * ratio))
                    height = int(round(original_height * ratio))
                    image = Image.open(file.image.path)
                    image.thumbnail((width, height), Image.ANTIALIAS)
                    image.save(file.image.thumbnail.path)
                    #imagefit.save(file.image.thumbnail.path)
                    print 'File ' + file.image.thumbnail.path + ' resized. Ratio = ', ratio
                except Exception as e:
                    print e
