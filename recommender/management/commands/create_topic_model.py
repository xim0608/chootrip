from django.core.management.base import BaseCommand
import time
from socket import gethostname
from datetime import datetime
from recommender.lib.models import TopicModel, Corpus
from django.conf import settings
import glob
import os


class Command(BaseCommand):
    help = 'import spot and review data to mongodb'

    def add_arguments(self, parser):
        parser.add_argument(
            '--corpus', dest='corpus_created_at', required=False,
            help='model created_at',
        )
        parser.add_argument(
            '--num_topics', dest='num_topics', required=True,
            help='num of topics',
        )

    def get_latest_saved_corpus(self):
        ls = glob.glob(settings.BASE_DIR + "/recommender/lib/corpus/*")
        times = [os.path.getctime(file) for file in ls]
        idx = times.index(max(times))
        latest_dir_name = ls[idx]
        latest_dir_time = latest_dir_name.split('/')[-1]
        return latest_dir_time

    def handle(self, *args, **options):
        start = time.time()
        try:
            if options['corpus_created_at']:
                created_at = datetime.strptime(options['corpus_created_at'], '%Y%m%d%H%M%S')
                corpus = Corpus(created_at=created_at)
                TopicModel(num_topics=options['num_topics'], corpus=corpus)
            else:
                # get latest corpus
                created_at = datetime.strptime(self.get_latest_saved_corpus(), '%Y%m%d%H%M%S')
                corpus = Corpus(created_at=created_at)
                TopicModel(num_topics=options['num_topics'], corpus=corpus)
        except Exception as e:
            import traceback
            from recommender.lib.notifications import Slack
            print(traceback.print_exc())
            Slack.notify("<!channel>\n{}\nScript has stopped in {}".format(str(type(e)), gethostname()))

        elapsed_time = time.time() - start
        print("elapsed_time:{0}".format(elapsed_time) + "[sec]")
