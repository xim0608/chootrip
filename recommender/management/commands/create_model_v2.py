from django.core.management.base import BaseCommand
import time
from socket import gethostname
from recommender.lib.models import Corpus, TopicModel
from django.conf import settings
import yaml
import os


class Command(BaseCommand):
    help = 'create lda'

    def handle(self, *args, **options):
        start = time.time()
        try:
            f = open(settings.BASE_DIR + "/recommender/lib/topic_settings.yml", "r+")
            topic_setting = yaml.load(f)
            created_models = os.listdir(settings.BASE_DIR + "/recommender/lib/files/topic_model/")
            tasks = topic_setting.keys() - created_models
            for task in tasks:
                print("start {}".format(task))
                TopicModel(task, skip_load=True).create()
        except Exception as e:
            import traceback
            from recommender.lib.notifications import Slack
            print(traceback.print_exc())
            Slack.notify("<!channel>\n{}\nScript has stopped in {}".format(str(type(e)), gethostname()))

        elapsed_time = time.time() - start
        print("elapsed_time:{0}".format(elapsed_time) + "[sec]")
