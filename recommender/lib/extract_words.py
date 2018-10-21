import re


def include_num(word):
    if re.search('[0-9]', word):
        return True
    return False


def extract_neologd_nouns(review):
    review_words = []
    for node_with_feature in review:
        if node_with_feature[0] == '名詞' and not include_num(node_with_feature[6]):
            if node_with_feature[1] == '一般' or node_with_feature[1] == 'サ変接続' or \
                    (node_with_feature[1] == '固有名詞' and not node_with_feature[2] == '人名' and not node_with_feature[2] == '地域'):
                review_words.append(node_with_feature[6])
    return review_words
