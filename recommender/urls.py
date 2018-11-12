from rest_framework import routers
from .views import SpotViewSet
from locations.views import PrefectureViewSet

router = routers.DefaultRouter()
router.register(r'spots', SpotViewSet)
router.register(r'prefectures', PrefectureViewSet)
