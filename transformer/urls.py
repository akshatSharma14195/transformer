from django.conf.urls import url
from . import views

app_name = 'transformer'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^map/(?P<access_key>[0-9a-f]{8}-?[0-9a-f]{4}-?4[0-9a-f]{3}-?[89ab][0-9a-f]{3}-?[0-9a-f]{12})$', views.transform),
    url(r'view_logs/', views.viewlogs, name='view_logs'),
    url(r'get_logs/', views.get_logs, name='get_logs'),
]
