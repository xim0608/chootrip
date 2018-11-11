from rest_framework import routers
from .views import SpotViewSet

router = routers.DefaultRouter()
router.register(r'spots', SpotViewSet)
