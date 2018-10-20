from django.core.management.base import BaseCommand
import time
from socket import gethostname
from datetime import datetime
from recommender.lib.models import TopicModel, Corpus


class Command(BaseCommand):
    help = 'import spot and review data to mongodb'

    def add_arguments(self, parser):
        parser.add_argument(
            '--load_json', dest='load_json', required=False,
            help='num of topics',
        )

    def handle(self, *args, **options):
        start = time.time()
        try:
            if options['load_json'] == "True":
                Corpus(load_json=True)
            else:
                Corpus()
        except Exception as e:
            import traceback
            from recommender.lib.notifications import Slack
            print(traceback.print_exc())
            Slack.notify("<!channel>\n{}\nScript has stopped in {}".format(str(type(e)), gethostname()))

        elapsed_time = time.time() - start
        print("elapsed_time:{0}".format(elapsed_time) + "[sec]")
