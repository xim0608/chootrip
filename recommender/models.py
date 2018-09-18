from django.db import models
from locations.models import City
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.fields import ArrayField


class Spot(models.Model):
    class Meta:
        db_table = 'spots'

    base_id = models.CharField(max_length=200, null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True)
    url = models.CharField(max_length=200, unique=True)
    count = models.IntegerField(default=0, null=True, blank=True)
    total_count = models.IntegerField(default=None, null=True, blank=True)
    all_lang_total_count = models.IntegerField(default=None, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_updatable = models.BooleanField(default=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    valid_area = models.BooleanField(default=False)

    def __str__(self):
        if self.count != 0:
            return 'spot={}, count={}/{}'.format(self.title, self.count, self.total_count)
        else:
            return 'url={}'.format(self.url)

    def update_count(self, count):
        self.count = self.count + count
        self.save()

    @classmethod
    def remained_tasks(cls):
        remained_tasks = Spot.objects.filter(total_count=None)
        doing_or_done_tasks = Spot.objects.exclude(total_count=None)
        remained_tasks_list = list(remained_tasks)
        doing_or_done_tasks_list = list(doing_or_done_tasks)
        if len(doing_or_done_tasks) > 0:
            for task in doing_or_done_tasks_list:
                if task.total_count - task.count > 0:
                    remained_tasks_list.append(task)
        return remained_tasks_list

    @classmethod
    def import_urls(cls, urls):
        for url in urls:
            Spot.objects.get_or_create(url=url)


@receiver(post_save, sender=Spot)
def create_spot(sender, instance, created, **kwargs):
    if created:
        # set spot base id
        tmp = instance.url.split('Attraction_Review-')[1].split('-Reviews')[0]
        instance.base_id = tmp
        if Spot.objects.filter(base_id=tmp).exists():
            instance.delete()
        else:
            instance.save()


class SpotImage(models.Model):
    class Meta:
        db_table = 'spot_images'

    spot = models.ForeignKey(Spot, on_delete=models.CASCADE)
    url = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    license = models.IntegerField()
    height = models.IntegerField()
    width = models.IntegerField()
    owner = models.CharField(max_length=255)
    owner_name = models.CharField(max_length=255)


class Review(models.Model):
    class Meta:
        db_table = 'reviews'

    username = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    content = models.TextField()
    rating = models.IntegerField()
    ta_id = models.IntegerField(unique=True, default=None)
    rating_date = models.CharField(max_length=200, default='')
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE)

    def __str__(self):
        return 'spot={}, title={}'.format(self.spot.title, self.title)


class AnalyzedReview(models.Model):
    class Meta:
        db_table = 'analyzed_reviews'

    review = models.OneToOneField(
        Review,
        on_delete=models.CASCADE,
        primary_key=True
    )
    mecab_neologd = ArrayField(
        ArrayField(
            models.CharField(max_length=255, default=None)
            , blank=True)
        , blank=True, null=True)
