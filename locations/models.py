from django.db import models


class Prefecture(models.Model):
    class Meta:
        db_table = 'prefectures'
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    name_kana = models.CharField(max_length=50)
    lat = models.DecimalField(max_digits=9, decimal_places=6, default=0)
    lon = models.DecimalField(max_digits=9, decimal_places=6, default=0)


class PrefectureAppend(models.Model):
    class Meta:
        db_table = 'prefecture_appends'
    prefecture = models.OneToOneField(
        Prefecture,
        on_delete=models.CASCADE,
        primary_key=True
    )
    base_id = models.CharField(max_length=255, unique=True)


class City(models.Model):
    class Meta:
        db_table = 'cities'
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    name_kana = models.CharField(max_length=50)
    lat = models.DecimalField(max_digits=9, decimal_places=6, default=0)
    lon = models.DecimalField(max_digits=9, decimal_places=6, default=0)
    prefecture = models.ForeignKey(Prefecture, on_delete=models.PROTECT)

    def _get_url(self):
        return 'https://www.tripadvisor.jp/Attractions-' + self.cityappend.ta_area_id + '.html'
    url = property(_get_url)


class CityAppend(models.Model):
    class Meta:
        db_table = 'city_appends'
    city = models.OneToOneField(
        City,
        on_delete=models.CASCADE,
        primary_key=True
    )
    ta_area_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    finish = models.BooleanField(default=False)
