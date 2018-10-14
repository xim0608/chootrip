from django.core.management.base import BaseCommand
from recommender.models import AnalyzedReview, Spot
import time
from django.conf import settings
from datetime import datetime
import json


class Command(BaseCommand):
    help = 'create data frame'

    def handle(self, *args, **options):
        start = time.time()

        spots = Spot.objects.all()
        json_data = {}
        for spot in spots:
            contents = []
            a_r = AnalyzedReview.objects.filter(review__spot__id=spot.id).only('neologd_title', 'neologd_content')
            for r in a_r:
                contents.append(r.neologd_title)
                contents.append(r.neologd_content)
            json_data[spot.id] = contents
        file_path = settings.BASE_DIR + "/recommender/lib/files/jsons/{}.pkl".format(datetime.now().strftime('%Y%m%d%H%M%S'))
        f = open(file_path, 'w')
        json.dump(json_data, f)
        elapsed_time = time.time() - start
        print("elapsed_time:{0}".format(elapsed_time) + "[sec]")
