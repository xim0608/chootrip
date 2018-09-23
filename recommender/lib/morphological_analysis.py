from recommender.models import Review, AnalyzedReview
from recommender.lib.preprocess.normalization_neologd import normalize_neologd
import MeCab
from recommender.lib.notifications import Slack


class Analysis:
    def __init__(self, reviews_id=Review.objects.all().values('id')):
        self.reviews_id = reviews_id

    @classmethod
    def concat_title_and_content(cls, title, content):
        return "{0} {1}".format(title, content)

    def analysis_and_save(self):
        raise NotImplementedError


class AnalysisMecab(Analysis):
    def __init__(self, reviews_id=Review.objects.filter(analyzedreview__mecab_neologd__isnull=True).values('id')):
        super().__init__(reviews_id)
        self.mecab = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')

    def analysis_and_save(self):
        counter = 0
        for review_id in self.reviews_id:
            review = Review.objects.get(id=review_id['id'])
            content = normalize_neologd(review.content)
            title = normalize_neologd(review.title)
            input_data = self.concat_title_and_content(title, content)
            tokens = []
            node = self.mecab.parseToNode(input_data)
            while node:
                token = node.feature.split(',')
                if len(token) != 9:
                    # print("error token in {}".format(token))
                    pass
                else:
                    tokens.append(token)
                node = node.next
            AnalyzedReview.objects.update_or_create(
                review_id=review.id, defaults={'mecab_neologd': tokens}
            )

            counter += 1
            if counter % 1000 == 0:
                Slack.notify("mecab count: {}".format(counter))


class AnalysisJuman(Analysis):
    def __init__(self, reviews=Review.objects.filter(analyzedreview__jumanpp__isnull=True)):
        super().__init__(reviews)
        from pyknp import Jumanpp
        self.jumanpp = Jumanpp()

    def analysis_and_save(self):
        # num_of_reviews = self.reviews.count()
        for i, review in enumerate(self.reviews):
            input_data = self.concat_title_and_content(review.title, review.content)
            tokens = []
            try:
                result = self.jumanpp.analysis(input_data)
            except ValueError:
                result = self.jumanpp.analysis(input_data.replace(' ', '　'))
            except Exception:
                print("skip id: {}".format(review.id))
                continue

            for mrph in result.mrph_list():
                tokens.append(
                    [mrph.midasi, mrph.yomi, mrph.genkei, mrph.hinsi, mrph.bunrui,
                     mrph.katuyou1, mrph.katuyou2, mrph.imis, mrph.repname]
                )
            AnalyzedReview.objects.update_or_create(
                review_id=review.id,
                defaults={'jumanpp': tokens}
            )

            if i % 1000 == 0:
                Slack.notify("jumanpp count: {}".format(i))
