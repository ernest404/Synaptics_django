from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name = 'index'),
    path("analyze", views.analyze, name = 'analyze'),
    path("summarize", views.summarize, name =  'summarize'),
    path("download_report", views.download_report, name = 'download_report'),
]