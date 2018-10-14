from django.core.management.base import BaseCommand
from recommender.models import Review, AnalyzedReview, Spot
from django.db import connection
import pandas as pd
from recommender.lib.morphological_analysis import AnalysisMecab, AnalysisJuman
import time
from django.conf import settings
from socket import gethostname
from django.db.models import F
from datetime import datetime


def get_neologd(index):
    a_reviews = AnalyzedReview.objects.filter(review__spot__id=index.name).only('neologd_title',
                                                                                'neologd_content')
    contents = []
    for a_r in a_reviews:
        contents.append(a_r.neologd_title)
        contents.append(a_r.neologd_content)
    return contents


def get_juman(index):
    a_reviews = AnalyzedReview.objects.filter(review__spot__id=index.name).only('jumanpp_title',
                                                                                'jumanpp_content')
    contents = []
    for a_r in a_reviews:
        contents.append(a_r.jumanpp_title)
        contents.append(a_r.jumanpp_content)
    return contents


class Command(BaseCommand):
    help = 'create data frame'

    def handle(self, *args, **options):
        start = time.time()

        query = str(Spot.objects.all().query)
        spots = pd.read_sql_query(query, con=connection, index_col='id')

        spots = spots.assign(
            neologd=spots.apply(lambda x: get_neologd(x), axis=1),
            juman=spots.apply(lambda x: get_juman(x), axis=1)
        )

        file_path = settings.BASE_DIR + "/recommender/lib/files/df/{}.pkl".format(datetime.now().strftime('%Y%m%d%H%M%S'))
        spots.to_pickle(file_path)
        elapsed_time = time.time() - start
        print("elapsed_time:{0}".format(elapsed_time) + "[sec]")
