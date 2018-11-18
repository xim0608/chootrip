from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as dfr_filters
from rest_framework import viewsets, filters, pagination
from recommender.lib.models import TopicModel, Recommend
import json
import numpy as np
from django.http import JsonResponse

from .models import Spot
from .serializer import SpotSerializer


class SpotSetPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class SpotSearchFilter(dfr_filters.FilterSet):
    title = dfr_filters.CharFilter(name="title", lookup_expr='contains')

    class Meta:
        model = Spot
        fields = ['title']


class SpotViewSet(viewsets.ModelViewSet):
    queryset = Spot.objects.filter(count__gte=15).prefetch_related("spotimage_set")
    serializer_class = SpotSerializer
    # pagination_class = SpotSetPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter)
    filter_fields = ('city', 'id', 'title')
    filterset_fields = {
        'city': ('exact', 'in'),
        'id': ('exact', 'in'),
        'title': ('icontains',),
    }
    ordering_fields = ('count',)
    ordering = ('-count',)


topic_model = TopicModel('noun_30')
recommend_model = Recommend(topic_model)


def recommend(request):
    # 1. ユーザの選択したスポットIDのリストを受け取る
    data = json.loads(request.body.decode("utf-8"))
    user_favorite_spot_ids = data['spot_ids']

    # 2. ユーザの嗜好ベクトルを生成する
    user_vec_list = recommend_model.user_vec_list(user_favorite_spot_ids)
    sparsed_user_vec = recommend_model.user_vec_list_to_sparse(user_vec_list)

    # 3. 嗜好ベクトルを表示向けに標準化する
    np_user_vec = np.array(user_vec_list)
    np_user_vec_mean = np_user_vec.mean(keepdims=True)
    np_user_vec_std = np.std(np_user_vec, keepdims=True)
    normalized_user_vec = list((np_user_vec - np_user_vec_mean) / np_user_vec_std)

    # 3. Get Nearest Neighbor
    similarities = recommend_model.index[sparsed_user_vec]

    # 4. doc_id, 類似度のベクトルをdict型{'spot_id': 類似度}に変換する
    similarities_dict = {}
    for index, simirality in np.ndenumerate(similarities):
        doc_id = index[0]
        # convert doc_id to spot_id
        spot_id = recommend_model.corpus_model.convert_id(doc_id=doc_id)
        # implicit convert numpy.float32 to float
        similarities_dict[spot_id] = float(simirality)

    # 5. 類似度順にソートする(疎ベクトルの形になる)
    # similarities_sorted = sorted(similarities_dict.items(), key=lambda x: -x[1])

    # 6. 類似度ソートリストと，ユーザ嗜好ベクトルを返す
    return JsonResponse(
        {'similarities': similarities_dict, 'user_vec': sparsed_user_vec, 'normalized_user_vec': normalized_user_vec}
    )


def topics(request):
    topics_dict = {}
    for i in range(0, recommend_model.topic_model.lda.num_topics):
        topic = recommend_model.topic_model.lda.show_topic(i)
        topic = [(term[0], float(term[1])) for term in topic]
        topics_dict[i] = topic

    return JsonResponse(
        {'topics': topics_dict}
    )
