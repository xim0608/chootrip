import slackweb
from chootrip import settings


class Slack:
    slack = slackweb.Slack(url=settings.SLACK_WEBHOOK_URL)

    @classmethod
    def notify(cls, message):
        cls.slack.notify(text=message)
