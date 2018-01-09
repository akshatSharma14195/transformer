from django.conf.urls import url
from . import views
from .models import URLMapper

urlpatterns = [
    url(r'^$', views.index, name='index'),
]

url_prefix = 'map'

try:
    for url_map in URLMapper.objects.all():
        urlpatterns += [url(r'^' + '{}/{}'.format(url_prefix, url_map.access_key) + '$', views.transform)]

except Exception as e:
    print "Unexpected error", e

