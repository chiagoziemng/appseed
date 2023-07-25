# site_administrator/urls.py

from django.urls import path
from .views import ActivityLogView

urlpatterns = [
    path('activity-log/', ActivityLogView.as_view(), name='activity_log'),
]
