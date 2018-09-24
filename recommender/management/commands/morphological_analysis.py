from django.core.management.base import BaseCommand
from recommender.lib.morphological_analysis import *
import time
from socket import gethostname


class Command(BaseCommand):
    help = 'import spot and review data to mongodb'

    def add_arguments(self, parser):
        parser.add_argument(
            '--method', dest='method', required=False,
            help='nlp method type',
        )

    def handle(self, *args, **options):
        start = time.time()
        try:
            if options['method'] == 'mecab':
                AnalysisMecab().analysis_and_save()
            elif options['method'] == 'jumanpp':
                AnalysisJuman().analysis_and_save()
        except Exception as e:
            import traceback
            from recommender.lib.notifications import Slack
            print(traceback.print_exc())
            Slack.notify("<!channel>\n{}\nScript has stopped in {}".format(str(type(e)), gethostname()))

        elapsed_time = time.time() - start
        print("elapsed_time:{0}".format(elapsed_time) + "[sec]")
