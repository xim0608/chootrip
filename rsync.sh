#!/bin/sh

rsync -r ./recommender/lib/files/corpus batch0201.asia-northeast1-b.chootrip:/home/ryuki/chootrip/recommender/lib/files/corpus
rsync -r ./recommender/lib/files/similarities_index batch0201.asia-northeast1-b.chootrip:/home/ryuki/chootrip/recommender/lib/files/similarities_index
rsync -r ./recommender/lib/files/topic_model batch0201.asia-northeast1-b.chootrip:/home/ryuki/chootrip/topic_model
