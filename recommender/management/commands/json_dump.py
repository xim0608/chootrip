from django.core.management.base import BaseCommand
from recommender.models import AnalyzedReview, Spot
import time
from django.conf import settings
from datetime import datetime
import json


class Command(BaseCommand):
    help = 'create data frame'

    def add_arguments(self, parser):
        parser.add_argument(
            '--method', dest='method', required=True,
            help='morphological analysis method',
        )

    def handle(self, *args, **options):
        start = time.time()

        spots = Spot.objects.all()
        json_data = {}
        data_count = 1

        if options['method'] == 'neologd':
            for spot in spots:
                contents = []
                a_r = AnalyzedReview.objects.filter(review__spot__id=spot.id).only('neologd_title', 'neologd_content')
                for r in a_r:
                    contents.append(r.neologd_title)
                    contents.append(r.neologd_content)
                json_data[spot.id] = contents
                if spot.id % 1000 == 0:
                    file_path = settings.BASE_DIR + "/recommender/lib/files/jsons/neologd/{}.json".format(data_count)
                    f = open(file_path, 'w')
                    json.dump(json_data, f)
                    json_data = {}
                    data_count += 1
            file_path = settings.BASE_DIR + "/recommender/lib/files/jsons/neologd/{}.json".format(data_count)
            f = open(file_path, 'w')
            json.dump(json_data, f)
        elif options['method'] == 'jumanpp':
            for spot in spots:
                contents = []
                a_r = AnalyzedReview.objects.filter(review__spot__id=spot.id).only('jumanpp_title', 'jumanpp_content')
                for r in a_r:
                    contents.append(r.jumanpp_title)
                    contents.append(r.jumanpp_content)
                json_data[spot.id] = contents
                if spot.id % 1000 == 0:
                    file_path = settings.BASE_DIR + "/recommender/lib/files/jsons/jumanpp/{}.json".format(data_count)
                    f = open(file_path, 'w')
                    json.dump(json_data, f)
                    json_data = {}
                    data_count += 1
            file_path = settings.BASE_DIR + "/recommender/lib/files/jsons/jumanpp/{}.json".format(data_count)
            f = open(file_path, 'w')
            json.dump(json_data, f)
        elapsed_time = time.time() - start
        print("elapsed_time:{0}".format(elapsed_time) + "[sec]")
