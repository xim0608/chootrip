from recommender.lib import morphological_analysis
from gensim import corpora, models
from django.conf import settings
import logging
import glob
import json
import yaml
import os
from recommender.lib import extract_words

logging.basicConfig(format='%(levelname)s : %(message)s', level=logging.INFO)
logging.root.level = logging.INFO

f = open(settings.BASE_DIR + "/recommender/lib/corpus_settings.yml", "r+")
corpus_setting = yaml.load(f)

f = open(settings.BASE_DIR + "/recommender/lib/topic_settings.yml", "r+")
topic_setting = yaml.load(f)


class Corpus:
    def __init__(self, name):
        self.name = name
        self.settings = corpus_setting[name]
        self.no_below = self.settings['no_below']
        self.no_above = self.settings['no_above']
        self.extract_words_method = self.settings['extract_words_method']
        self.morphological_analysis = self.settings['morphological_analysis']
        self.dir = settings.BASE_DIR + "/recommender/lib/files/corpus/{}/".format(name)
        self.corpus = None
        self.dict = None
        self.spot_documents_words = []

        if os.path.isdir(self.dir):
            self.load_exist_models()

    # def extract_words(self):
    #     analyzed_review = AnalyzedReview.objects.all().only('neologd_title', 'neologd_content')
    #     for spot in Spot.objects.all().prefetch_related(
    #             Prefetch('review_set', queryset=Review.objects.all().only('id'), to_attr='reviews')):
    #         # words list including this spot review
    #         ids = [r.id for r in spot.reviews]
    #         reviews = analyzed_review.filter(review_id__in=ids)
    #         for review in reviews:
    #             self.spot_documents_words.append(morphological_analysis.extract_neologd_word(review))

    def extract_words_from_json(self):
        # get latest dumped files
        files = self.get_dumped_files()
        for file in files:
            f = open(file)
            data = json.load(f)
            for spot_id, reviews in data.items():
                spot_document_words = []
                for review in reviews:
                    spot_document_words.extend(getattr(extract_words, self.extract_words_method)(review))
                self.spot_documents_words.append(spot_document_words)
            f.close()

    def get_dumped_files(self):
        files = glob.glob(settings.BASE_DIR + "/recommender/lib/files/jsons/{}/*.json".format(self.morphological_analysis))
        return files

    def create_dictionary(self):
        self.dict = corpora.Dictionary(self.spot_documents_words)
        self.dict.filter_extremes(no_below=int(self.no_below), no_above=float(self.no_above))
        self.dict.save_as_text(self.dir + "dict.txt")

    def create_corpus(self):
        self.corpus = [self.dict.doc2bow(text) for text in self.spot_documents_words]
        corpora.MmCorpus.serialize(self.dir + "cop.mm", self.corpus)

    def load_exist_models(self):
        self.dict = corpora.Dictionary.load_from_text(self.dir + 'dict.txt')
        self.corpus = corpora.MmCorpus(self.dir + 'cop.mm')

    def create(self):
        if os.path.isdir(self.dir):
            os.removedirs(self.dir)
        os.mkdir(self.dir)
        # self.extract_words()
        self.extract_words_from_json()
        self.create_dictionary()
        self.create_corpus()

    # def create_from_json(self):
    #     self.extract_words_from_json()
    #     self.create_dictionary()
    #     self.create_corpus()


class TopicModel:
    def __init__(self, name):
        self.name = name
        self.settings = topic_setting[name]
        self.dir = settings.BASE_DIR + "/recommender/lib/files/topic_model/{}/".format(name)
        self._corpus = Corpus(self.settings['corpus'])
        self.num_topics = int(self.settings['num_topics'])
        self.dict = None
        self.corpus = None
        self.lda = None
        if os.path.isdir(self.dir):
            self.load_exist_models()

    def create_lda_model(self, num_topics):
        if self.corpus is None:
            raise ValueError("cannot compute LDA (no corpus)")
        self.dict = self._corpus.dict
        self.corpus = self._corpus.corpus
        self.lda = models.ldamodel.LdaModel(
            corpus=self.corpus, num_topics=num_topics, id2word=self.dict, update_every=0, passes=10)
        self.lda.save(self.dir + "lda.model")

    def create(self):
        if os.path.isdir(self.dir):
            os.removedirs(self.dir)
        os.mkdir(self.dir)
        self.create_lda_model(self.num_topics)

    def load_exist_models(self):
        self.lda = models.LdaModel.load(self.dir + 'lda.model')
