from django.core.management.base import BaseCommand
import time
from socket import gethostname
from datetime import datetime
from recommender.lib.topic_model import TopicModel


class Command(BaseCommand):
    help = 'import spot and review data to mongodb'

    def add_arguments(self, parser):
        parser.add_argument(
            '--created_at', dest='created_at', required=False,
            help='model created_at',
        )
        parser.add_argument(
            '--num_topics', dest='num_topics', required=True,
            help='num of topics',
        )

    def handle(self, *args, **options):
        start = time.time()
        try:
            if options['created_at']:
                created_at = datetime.strptime(options['created_at'], '%Y%m%d%H%M%S')
                TopicModel(num_topics=options['num_topics'], created_at=created_at)
            else:
                TopicModel(num_topics=options['num_topics'])
        except Exception as e:
            import traceback
            from recommender.lib.notifications import Slack
            print(traceback.print_exc())
            Slack.notify("<!channel>\n{}\nScript has stopped in {}".format(str(type(e)), gethostname()))

        elapsed_time = time.time() - start
        print("elapsed_time:{0}".format(elapsed_time) + "[sec]")
