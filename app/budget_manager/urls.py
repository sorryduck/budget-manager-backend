from django.urls import path
from .views import *

urlpatterns = [
    path('table-data/', TableData.as_view()),
    path('stats-data/', StatisticData.as_view()),
    path('user-data/', UserData.as_view()),
]
