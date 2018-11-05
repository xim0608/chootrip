from django.core.management.base import BaseCommand
import time
from socket import gethostname
from recommender.lib.models import Corpus, TopicModel


class Command(BaseCommand):
    help = 'import spot and review data to mongodb'

    def add_arguments(self, parser):
        parser.add_argument(
            '--corpus', dest='corpus', required=False,
            help='corpus',
        )
        parser.add_argument(
            '--topic', dest='topic', required=False,
            help='topic_model',
        )

    def handle(self, *args, **options):
        start = time.time()
        try:
            if options['topic']:
                TopicModel(options['topic']).create()
            elif options['corpus']:
                Corpus(name=options['corpus'], skip_load=True).create()
        except Exception as e:
            import traceback
            from recommender.lib.notifications import Slack
            print(traceback.print_exc())
            Slack.notify("<!channel>\n{}\nScript has stopped in {}".format(str(type(e)), gethostname()))

        elapsed_time = time.time() - start
        print("elapsed_time:{0}".format(elapsed_time) + "[sec]")
