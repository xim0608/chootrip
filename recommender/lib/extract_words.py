import re
import urllib
from nltk.corpus import stopwords as nltk_stopwords


def include_num(word):
    if re.search('[0-9]', word):
        return True
    return False


def __get_sloth_lib_stop_words():
    slothlib_path = 'http://svn.sourceforge.jp/svnroot/slothlib/CSharp/Version1/SlothLib/NLP/Filter/StopWord/word/Japanese.txt'
    slothlib_file = urllib.request.urlopen(slothlib_path)
    slothlib_stopwords = [line.decode("utf-8").strip() for line in slothlib_file if line.decode("utf-8").strip() != '']
    return slothlib_stopwords


def get_stop_words():
    stopwords = ['\n', '、', '「', '」', '（', '）']
    stopwords += __get_sloth_lib_stop_words()
    stopwords += nltk_stopwords.words('english')
    stopwords += list(map(lambda w: w.upper(), nltk_stopwords.words('english')))
    print('created stopwords_list')
    return stopwords


stopwords = get_stop_words()


def extract_neologd_nouns(review):
    review_words = []
    for node_with_feature in review:
        if node_with_feature[0] == '名詞' and not include_num(node_with_feature[6]) and not node_with_feature[6] in stopwords:
            if node_with_feature[1] == '一般' or node_with_feature[1] == 'サ変接続' or \
                    (node_with_feature[1] == '固有名詞' and not node_with_feature[2] == '人名' and not node_with_feature[2] == '地域'):
                review_words.append(node_with_feature[6])
    return review_words


def extract_nouns_and_adjectives(review):
    review_words = []
    for node_with_feature in review:
        if not include_num(node_with_feature[6]) and not node_with_feature[6] in stopwords:
            if node_with_feature[0] == '名詞':
                if node_with_feature[1] == '一般' or node_with_feature[1] == 'サ変接続' or \
                    (node_with_feature[1] == '固有名詞' and not node_with_feature[2] == '人名' and not node_with_feature[
                                                                                                     2] == '地域'):
                    review_words.append(node_with_feature[6])
            elif node_with_feature[0] == '形容詞':
                if node_with_feature[1] == '自立':
                    review_words.append(node_with_feature[6])
    return review_words
