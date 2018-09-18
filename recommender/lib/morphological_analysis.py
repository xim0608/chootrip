from recommender.models import Review, AnalyzedReview
from recommender.lib.preprocess.normalization_neologd import normalize_neologd
import MeCab
from recommender.lib.notifications import Slack


class Analysis:
    def __init__(self, reviews=Review.objects.all()):
        self.reviews = reviews
        print("Review Count: {}".format(reviews.count()))

    @classmethod
    def concat_title_and_content(cls, title, content):
        return "{0} {1}".format(title, content)

    def analysis_and_save(self):
        raise NotImplementedError


class AnalysisMecab(Analysis):
    def __init__(self, reviews=Review.objects.filter(analyzedreview__mecab_neologd__isnull=True)):
        super().__init__(reviews)
        self.mecab = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')

    def analysis_and_save(self):
        for review in self.reviews:
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


class AnalysisJuman(Analysis):
    def __init__(self, reviews=Review.objects.filter(analyzedreview__jumanpp__isnull=True)):
        super().__init__(reviews)
        from pyknp import Jumanpp
        self.jumanpp = Jumanpp()

    def analysis_and_save(self):
        num_of_reviews = self.reviews.count()
        for i, review in enumerate(self.reviews):
            input_data = self.concat_title_and_content(review.title, review.content)
            tokens = []
            try:
                result = self.jumanpp.analysis(input_data)
            except ValueError:
                result = self.jumanpp.analysis(input_data.replace(' ', '　'))
                print('value error replacing space')

            for mrph in result.mrph_list():
                tokens.append(
                    [mrph.midasi, mrph.yomi, mrph.genkei, mrph.hinsi, mrph.bunrui,
                     mrph.katuyou1, mrph.katuyou2, mrph.imis, mrph.repname]
                )
            a_r = AnalyzedReview.objects.get(review_id=review.id)
            a_r.jumanpp = tokens
            a_r.save()

            if i % 10 == 0:
                Slack.notify("count: {}/{}".format(i, num_of_reviews))

