from django.core.management.base import BaseCommand
from recommender.lib.morphological_analysis import *
import time
from socket import gethostname
from django.db.models import F


class Command(BaseCommand):
    help = 'import spot and review data to mongodb'

    def add_arguments(self, parser):
        parser.add_argument(
            '--method', dest='method', required=True,
            help='nlp method type',
        )
        parser.add_argument(
            '--q', dest='mod_filter', required=False,
            help='nlp method query',
        )

    def handle(self, *args, **options):
        start = time.time()
        try:
            if options['method'] == 'mecab':
                AnalysisMecab().analysis_and_save()
            elif options['method'] == 'jumanpp':
                if options['mod_filter']:
                    remain, mod = options['mod_filter'].split('/')
                    remain = int(remain)
                    mod = int(mod)
                    reviews_id = Review.objects.annotate(
                        idmod=F('review_id') % mod
                    ).filter(analyzedreview__jumanpp_content__isnull=True, idmod=remain).values('id')
                    AnalysisJuman(reviews_id=reviews_id).analysis_and_save()
                else:
                    AnalysisJuman().analysis_and_save()
        except Exception as e:
            import traceback
            from recommender.lib.notifications import Slack
            print(traceback.print_exc())
            Slack.notify("<!channel>\n{}\nScript has stopped in {}".format(str(type(e)), gethostname()))

        elapsed_time = time.time() - start
        print("elapsed_time:{0}".format(elapsed_time) + "[sec]")
