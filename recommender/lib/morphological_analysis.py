from recommender.models import Review, AnalyzedReview
from recommender.lib.preprocess.normalization_neologd import normalize_neologd
import MeCab


class Analysis:
    def __init__(self, reviews=Review.objects.all()):
        self.reviews = reviews

    @classmethod
    def concat_title_and_content(cls, title, content):
        return "{0} {1}".format(title, content)

    def analysis_and_save(self):
        raise NotImplementedError


class AnalysisMecab(Analysis):
    def __init__(self, reviews=Review.objects.all()):
        super().__init__(reviews)
        self.mecab = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')

    def analysis_and_save(self):
        for review in self.reviews:
            if len(AnalyzedReview.objects.filter(review_id=review.id)) > 0:
                continue
            content = normalize_neologd(review.content)
            title = normalize_neologd(review.title)
            input_data = self.concat_title_and_content(title, content)
            tokens = []
            node = self.mecab.parseToNode(input_data)
            while node:
                token = node.feature.split(',')
                if len(token) != 9:
                    print("error token in {}".format(token))
                else:
                    tokens.append(token)
                node = node.next
            a_r = AnalyzedReview(review_id=review.id, mecab_neologd=tokens)
            a_r.save()
