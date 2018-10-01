from recommender.models import Review, AnalyzedReview, Spot
from django.db.models import Prefetch
from recommender.lib import morphological_analysis
from gensim import corpora, models, similarities
from datetime import datetime


class TopicModel:
    def __init__(self, created_at):
        self.created_at = datetime.now()

        self.corpus = None
        self.dict = None
        self.lda = None
        self.spot_documents_words = []

    def extract_words(self):
        analyzed_review = AnalyzedReview.objects.all().only('neologd_title', 'neologd_content')
        for spot in Spot.objects.all().prefetch_related(Prefetch('review_set', queryset=Review.objects.all().only('id'), to_attr='reviews')):
            # words list including this spot review
            ids = [r.id for r in spot.reviews]
            reviews = analyzed_review.filter(review_id__in=ids)
            for review in reviews:
                self.spot_documents_words.append(morphological_analysis.extract_neologd_word(review))

    def create_dictionaly(self):
        self.dict = corpora.Dictionary(self.spot_documents_words)
        self.dict.filter_extremes(no_below=2, no_above=0.3)
        self.dict.save_as_text("dict_{}.txt".format(self.created_at.strftime('%Y%m%d%H%M%S')))

    def create_corpus(self):
        self.corpus = [self.dict.doc2bow(text) for text in self.spot_documents_words]
        corpora.MmCorpus.serialize("cop_{}.mm".format(self.created_at.strftime('%Y%m%d%H%M%S')), self.corpus)

    def create_lda_model(self, num_topics):
        self.lda = models.ldamodel.LdaModel(corpus=self.corpus, num_topics=num_topics, id2word=self.dict)

    def save(self):
        self.lda.save("lda.model".format(self.created_at.strftime('%Y%m%d%H%M%S')))
