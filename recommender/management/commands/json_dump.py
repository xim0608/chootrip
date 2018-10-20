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
        created_at = datetime.now()
        json_data = {}
        data_count = 1
        for spot in spots:
            contents = []
            a_r = AnalyzedReview.objects.filter(review__spot__id=spot.id).only('neologd_title', 'neologd_content')
            for r in a_r:
                contents.append(r.neologd_title)
                contents.append(r.neologd_content)
            json_data[spot.id] = contents
            if spot.id % 1000 == 0:
                file_path = settings.BASE_DIR + "/recommender/lib/files/jsons/{}_{}.json".format(
                    created_at.strftime('%Y%m%d%H%M%S'), data_count)
                f = open(file_path, 'w')
                json.dump(json_data, f)
                json_data = {}
                data_count += 1
        file_path = settings.BASE_DIR + "/recommender/lib/files/jsons/{}_{}.json".format(
            datetime.now().strftime('%Y%m%d%H%M%S'), data_count)
        f = open(file_path, 'w')
        json.dump(json_data, f)
        elapsed_time = time.time() - start
        print("elapsed_time:{0}".format(elapsed_time) + "[sec]")
