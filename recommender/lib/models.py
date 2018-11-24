from gensim import corpora, models, similarities
from django.conf import settings
import logging
import glob
import json
import yaml
import os
from recommender.lib import extract_words
import shutil
import pickle

logging.basicConfig(format='%(levelname)s : %(message)s', level=logging.INFO)
logging.root.level = logging.INFO

f = open(settings.BASE_DIR + "/recommender/lib/corpus_settings.yml", "r+")
corpus_setting = yaml.load(f)

f = open(settings.BASE_DIR + "/recommender/lib/topic_settings.yml", "r+")
topic_setting = yaml.load(f)


class Corpus:
    def __init__(self, name, skip_load=False):
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
        # key: spot_id, value: doc_id
        self.id_conversion_table = {}

        # key: doc_id, value: spot_id
        self.doc_conversion_table = {}

        if os.path.isdir(self.dir) and not skip_load:
            self.load_exist_models()

    def convert_id(self, spot_id=None, doc_id=None):
        if (spot_id is None and doc_id is None) or (spot_id is not None and doc_id is not None):
            raise ValueError('Specify ONE variable.')
        if spot_id is not None:
            return self.id_conversion_table.get(spot_id)
        if doc_id is not None:
            # return dict index
            return self.doc_conversion_table.get(doc_id)
            # improve performance
            # for dict_spot_id, dict_doc_id in self.id_conversion_table.items():
            #     if dict_doc_id == doc_id:
            #         return int(dict_spot_id)
        raise ValueError("out of Index")

    def extract_words_from_json(self):
        # get latest dumped files
        files = self.get_dumped_json_files()
        for file in files:
            f = open(file)
            data = json.load(f)
            for spot_id, reviews in data.items():
                spot_document_words = []
                self.id_conversion_table[spot_id] = len(self.spot_documents_words)
                for review in reviews:
                    spot_document_words.extend(getattr(extract_words, self.extract_words_method)(review))
                self.spot_documents_words.append(spot_document_words)
            f.close()

    def get_dumped_json_files(self):
        # get morphological analyzed json data
        files = glob.glob(
            settings.BASE_DIR + "/recommender/lib/files/jsons/{}/*.json".format(self.morphological_analysis))
        return files

    def extract_words_from_pickles(self):
        # get latest dumped files
        files = self.get_dumped_pickles()
        for file in files:
            with open(file, mode='rb') as pickled_file:
                data = pickle.load(pickled_file)
                for spot_id, reviews in data.items():
                    spot_document_words = []
                    self.id_conversion_table[spot_id] = len(self.spot_documents_words)
                    for review in reviews:
                        spot_document_words.extend(getattr(extract_words, self.extract_words_method)(review))
                    self.spot_documents_words.append(spot_document_words)

    def get_dumped_pickles(self):
        # get morphological analyzed json data
        files = glob.glob(
            settings.BASE_DIR + "/recommender/lib/files/pickles/{}/*.pickle".format(self.morphological_analysis))
        return files

    def create_dictionary(self):
        self.dict = corpora.Dictionary(self.spot_documents_words)
        self.dict.filter_extremes(no_below=int(self.no_below), no_above=float(self.no_above))
        self.dict.save_as_text(self.dir + "dict.txt")

    def create_corpus(self):
        self.corpus = [self.dict.doc2bow(text) for text in self.spot_documents_words]
        corpora.MmCorpus.serialize(self.dir + "cop.mm", self.corpus)
        # also save id_conversion_table for convert corpus_id and spot_id
        with open(self.dir + "id_conversion_table.pickle", mode='wb') as f:
            pickle.dump(self.id_conversion_table, f)

    def load_exist_models(self):
        self.dict = corpora.Dictionary.load_from_text(self.dir + 'dict.txt')
        self.corpus = corpora.MmCorpus(self.dir + 'cop.mm')
        with open(self.dir + "id_conversion_table.pickle", mode='rb') as f:
            self.id_conversion_table = pickle.load(f)
        self.doc_conversion_table = {v: k for k, v in self.id_conversion_table.items()}

    def create(self):
        if os.path.isdir(self.dir):
            shutil.rmtree(self.dir)
        os.mkdir(self.dir)
        # self.extract_words()
        self.extract_words_from_pickles()
        self.create_dictionary()
        self.create_corpus()

    # def create_from_json(self):
    #     self.extract_words_from_json()
    #     self.create_dictionary()
    #     self.create_corpus()


class TopicModel:
    def __init__(self, name, skip_load=False):
        self.name = name
        self.settings = topic_setting[name]
        self.dir = settings.BASE_DIR + "/recommender/lib/files/topic_model/{}/".format(name)
        self.corpus_model = Corpus(self.settings['corpus'])
        self.num_topics = int(self.settings['num_topics'])
        self.alpha = self.settings.get('alpha')
        self.lda = None
        if os.path.isdir(self.dir) and not skip_load:
            self.load_exist_models()

    def create_lda_model(self, num_topics):
        if self.corpus_model is None:
            raise ValueError("cannot compute LDA (no corpus)")
        # self.lda = models.ldamodel.LdaModel(
        #     corpus=self.corpus_model.corpus, num_topics=num_topics,
        #     id2word=self.corpus_model.dict, update_every=0, passes=10)
        self.lda = models.ldamulticore.LdaMulticore(
            corpus=self.corpus_model.corpus, num_topics=num_topics,
            id2word=self.corpus_model.dict, batch=True, passes=10)
        self.lda.save(self.dir + "lda.model")

    def create(self):
        if os.path.isdir(self.dir):
            shutil.rmtree(self.dir)
        os.mkdir(self.dir)
        self.create_lda_model(self.num_topics)

    def load_exist_models(self):
        self.lda = models.LdaModel.load(self.dir + 'lda.model')


class Recommend:
    def __init__(self, topic_model: TopicModel):
        self.topic_model = topic_model
        self.corpus_model = topic_model.corpus_model
        self.dir = settings.BASE_DIR + "/recommender/lib/files/similarities_index/{}/".format(self.topic_model.name)
        self.index = None
        if os.path.isdir(self.dir):
            self.load_exist_index()
        else:
            self.create()

    def create(self):
        if os.path.isdir(self.dir):
            shutil.rmtree(self.dir)
        os.mkdir(self.dir)
        self.index = similarities.MatrixSimilarity(self.topic_model.lda[self.corpus_model.corpus])
        self.index.save(self.dir + 'similarities.index')

    def load_exist_index(self):
        self.index = similarities.MatrixSimilarity.load(self.dir + 'similarities.index')

    def get_vec(self, spot_id):
        converted_doc_id = self.corpus_model.convert_id(spot_id=spot_id)
        return self.topic_model.lda.get_document_topics(self.corpus_model.corpus[converted_doc_id], minimum_probability=0)

    def user_vec_list(self, spot_ids):
        user_vector_list = [0] * self.topic_model.lda.num_topics
        # 疎行列をpython list形式に変換する．
        for spot_id in spot_ids:
            # get spot vec
            spot_vector = self.get_vec(spot_id)
            for element in spot_vector:
                direction = element[0]
                el_magnitude = element[1]
                user_vector_list[direction] += el_magnitude
        return user_vector_list

    @classmethod
    def user_vec_list_to_sparse(cls, user_vector_list):
        # 疎行列に戻す
        sparse_user_vector = []
        for list_index, el_magnitude in enumerate(user_vector_list):
            sparse_user_vector.append((list_index, el_magnitude))
        return sparse_user_vector

    def get_spot_topic_words(self, spot_id):
        converted_doc_id = self.corpus_model.convert_id(spot_id=spot_id)
        return self.topic_model.lda.show_topics(converted_doc_id)
