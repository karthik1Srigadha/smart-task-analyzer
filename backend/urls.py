from django.contrib import admin
from django.urls import path, include

from django.http import JsonResponse

def home(request):
    return JsonResponse({"message": "Smart Task Analyzer API is running"})

urlpatterns = [
    path("", home),
    path("api/tasks/", include("tasks.urls")),
]
