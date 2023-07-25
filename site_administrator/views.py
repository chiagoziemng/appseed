# site_administrator/views.py

from django.shortcuts import render
from django.views import View
from .models import ActivityLog

class ActivityLogView(View):
    template_name = 'site_administrator/activity_log.html'

    def get(self, request):
        # Retrieve all activity log entries (you can customize this further if needed)
        activity_log_entries = ActivityLog.objects.all()

        return render(request, self.template_name, {'activity_log_entries': activity_log_entries})
