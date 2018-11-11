from django.core.management.base import BaseCommand
import os
from recommender.models import Spot, SpotImage
from django.db.models import Count

import time
import traceback

import flickrapi


class Command(BaseCommand):
    API_LIMIT_PER_HOUR = 3600

    def handle(self, *args, **options):
        flickr_api_key = os.environ.get('FLICKR_API_KEY')
        secret_key = os.environ.get('FLICKR_SECRET_KEY')

        # 画像がないSpotのみを取得する
        target_data = SpotImage.objects.all()
        groupby_data = target_data.values('spot_id').annotate(total=Count('spot_id')).order_by('total')
        spots_id = [x['spot_id'] for x in list(filter(lambda n: n['total'] > 0, list(groupby_data)))]
        spots = Spot.objects.exclude(id__in=spots_id).filter(count__gt=5)

        for spot in spots:
            keyword = spot.title.split(' (')[0].split('（')[0]

            flicker = flickrapi.FlickrAPI(flickr_api_key, secret_key, format='parsed-json')
            response = flicker.photos.search(
                text=keyword,
                per_page=50,
                media='photos',
                sort='relevance',
                safe_search=1,
                extras='url_m,license,owner_name',
                license='1,2,3,4,5,6'
            )
            print(response)
            photos = response['photos']
            time.sleep(1.5)
            try:
                for photo in photos['photo']:
                    url_m = photo['url_m']
                    height_m = photo['height_m']
                    width_m = photo['width_m']
                    license = photo['license']
                    title = photo['title']
                    owner = photo['owner']
                    owner_name = photo['ownername']
                    spot.spotimage_set.create(
                        url=url_m, height=height_m, width=width_m, license=license, title=title,
                        owner=owner, owner_name=owner_name
                    )

            except Exception as e:
                traceback.print_exc()
