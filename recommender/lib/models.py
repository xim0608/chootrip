from recommender.models import Review, AnalyzedReview, Spot
from django.db.models import Prefetch
from recommender.lib import morphological_analysis
from gensim import corpora, models, similarities
from datetime import datetime
import os
from django.conf import settings
import logging

logging.basicConfig(format='%(levelname)s : %(message)s', level=logging.INFO)
logging.root.level = logging.INFO


class Corpus:
    def __init__(self, created_at=datetime.now()):
        self.created_at = created_at
        self.dir = settings.BASE_DIR + "/recommender/lib/files/corpus/{}/".format(self.created_at.strftime('%Y%m%d%H%M%S'))
        self.corpus = None
        self.dict = None
        self.spot_documents_words = []

        if os.path.isdir(self.dir):
            self.load_exist_models()
        else:
            os.mkdir(self.dir)
            self.create()

    def extract_words(self):
        analyzed_review = AnalyzedReview.objects.all().only('neologd_title', 'neologd_content')
        for spot in Spot.objects.all().prefetch_related(
                Prefetch('review_set', queryset=Review.objects.all().only('id'), to_attr='reviews')):
            # words list including this spot review
            ids = [r.id for r in spot.reviews]
            reviews = analyzed_review.filter(review_id__in=ids)
            for review in reviews:
                self.spot_documents_words.append(morphological_analysis.extract_neologd_word(review))

    def create_dictionary(self):
        self.dict = corpora.Dictionary(self.spot_documents_words)
        self.dict.filter_extremes(no_below=2, no_above=0.3)
        self.dict.save_as_text(self.dir + "dict.txt")

    def create_corpus(self):
        self.corpus = [self.dict.doc2bow(text) for text in self.spot_documents_words]
        corpora.MmCorpus.serialize(self.dir + "cop.mm", self.corpus)

    def load_exist_models(self):
        self.dict = corpora.Dictionary.load_from_text(self.dir + 'dict.txt')
        self.corpus = corpora.MmCorpus(self.dir + 'cop.mm')

    def create(self):
        self.extract_words()
        self.create_dictionary()
        self.create_corpus()


class TopicModel:
    def __init__(self, num_topics=None, corpus=None, created_at=datetime.now()):
        self.created_at = created_at
        self.dir = settings.BASE_DIR + "/recommender/lib/files/topic_model/{}/".format(self.created_at.strftime('%Y%m%d%H%M%S'))
        self.corpus = corpus
        self.dict = None
        self.lda = None
        if os.path.isdir(self.dir):
            self.load_exist_models()
        else:
            # create model
            os.mkdir(self.dir)
            if num_topics is None:
                raise ValueError("cannot compute LDA (specify num topics)")
            self.create(num_topics)

    def create_lda_model(self, num_topics):
        if self.corpus is None:
            raise ValueError("cannot compute LDA (no corpus)")
        self.corpus = self.corpus.corpus
        self.dict = self.corpus.dict
        self.lda = models.ldamodel.LdaModel(
            corpus=self.corpus, num_topics=num_topics, id2word=self.dict, update_every=0, passes=10)
        self.lda.save(self.dir + "lda.model")

    def create(self, num_topics):
        self.create_lda_model(num_topics)

    def load_exist_models(self):
        self.lda = models.LdaModel.load(self.dir + 'lda.model')
