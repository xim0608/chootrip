from recommender.models import Review, AnalyzedReview
from recommender.lib.preprocess.normalization_neologd import normalize_neologd
import MeCab
from recommender.lib.notifications import Slack
import requests
from socket import gethostname
import re


def include_num(word):
    if re.search('[0-9]', word):
        return True
    return False


def extract_neologd_word(review):
    spot_words = []
    for node_with_feature in review.neologd_title + review.neologd_content:
        if node_with_feature[0] == '名詞':
            if node_with_feature[1] == '一般' or node_with_feature[1] == 'サ変接続' or \
                    (node_with_feature[1] == '固有名詞' and not node_with_feature[2] == '地域'):
                if not include_num(node_with_feature[6]) and not node_with_feature[6][-1] == '駅':
                    spot_words.append(node_with_feature[6])
    return spot_words


def extract_neologd_word_json(review):
    review_words = []
    for node_with_feature in review:
        if node_with_feature[0] == '名詞':
            if node_with_feature[1] == '一般' or node_with_feature[1] == 'サ変接続' or \
                    (node_with_feature[1] == '固有名詞' and not include_num(node_with_feature[6]) and not node_with_feature[2] == '人名' and not node_with_feature[2] == '地域'):
                review_words.append(node_with_feature[6])
    return review_words



class Analysis:
    def __init__(self, reviews_id=Review.objects.all().values('id')):
        self.reviews_id = reviews_id

    @classmethod
    def concat_title_and_content(cls, title, content):
        return "{0} {1}".format(title, content)

    def analysis_and_save(self):
        raise NotImplementedError


class AnalysisMecab(Analysis):
    def __init__(self, reviews_id=Review.objects.filter(analyzedreview__neologd_content__isnull=True).values('id')):
        super().__init__(reviews_id)
        self.mecab = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')

    def analysis_and_save(self):
        counter = 0
        for review_id in self.reviews_id:
            review = Review.objects.get(id=review_id['id'])
            content = normalize_neologd(review.content)
            title = normalize_neologd(review.title)

            # content
            content_tokens = []
            node = self.mecab.parseToNode(content)
            while node:
                token = node.feature.split(',')
                if len(token) != 9:
                    # print("error token in {}".format(token))
                    pass
                else:
                    content_tokens.append(token)
                node = node.next

            # title
            title_tokens = []
            node = self.mecab.parseToNode(title)
            while node:
                token = node.feature.split(',')
                if len(token) != 9:
                    # print("error token in {}".format(token))
                    pass
                else:
                    title_tokens.append(token)
                node = node.next

            # update neologd title and content
            AnalyzedReview.objects.update_or_create(
                review_id=review.id, defaults={'neologd_content': content_tokens, 'neologd_title': title_tokens}
            )

            if counter % 1000 == 0:
                Slack.notify("mecab count: {}, host: {}".format(counter, gethostname()))
            counter += 1


class AnalysisJuman(Analysis):
    def __init__(self, reviews_id=Review.objects.filter(analyzedreview__jumanpp_content__isnull=True).values('id')):
        super().__init__(reviews_id)

    def analysis_and_save(self):
        counter = 0
        for review_id in self.reviews_id:
            review = Review.objects.get(id=review_id['id'])
            content = normalize_neologd(review.content)
            title = normalize_neologd(review.title)

            # content
            replaced_content = content.replace('\\', '')
            if replaced_content:
                payload = {'string': replaced_content}
                content_res = requests.post('http://jumanpp-api/parse', data=payload)
                jumanpp_content = content_res.json()['results']
            else:
                jumanpp_content = []

            # title
            replaced_title = title.replace('\\', '')
            if replaced_title:
                payload = {'string': replaced_title}
                title_res = requests.post('http://jumanpp-api/parse', data=payload)
                jumanpp_title = title_res.json()['results']
            else:
                jumanpp_title = []

            try:
                AnalyzedReview.objects.update_or_create(
                    review_id=review.id,
                    defaults={'jumanpp_content': jumanpp_content,
                              'jumanpp_title': jumanpp_title}
                )
            except Exception as e:
                print("skip record review id: {}".format(review.id))
                print(e)
                continue

            if counter % 1000 == 0:
                Slack.notify("jumanpp count: {}, host: {}".format(counter, gethostname()))
            counter += 1
