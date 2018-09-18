from django.core.management.base import BaseCommand
from recommender.lib.morphological_analysis import *
import time

class Command(BaseCommand):
    help = 'import spot and review data to mongodb'

    def add_arguments(self, parser):
        parser.add_argument(
            '--method', dest='method', required=False,
            help='nlp method type',
        )

    def handle(self, *args, **options):
        start = time.time()
        if options['method'] == 'mecab':
            AnalysisMecab().analysis_and_save()
        elif options['method'] == 'jumanpp':
            AnalysisJuman().analysis_and_save()

        elapsed_time = time.time() - start
        print("elapsed_time:{0}".format(elapsed_time) + "[sec]")
