from django.conf.urls import url
from . import views

app_name = 'transformer'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^map/(?P<access_key>[0-9a-z-]+)/$', views.transform, name='map_url'),
    url(r'view_logs/', views.view_logs, name='view_logs'),
    url(r'get_logs/', views.get_logs, name='get_logs'),
    url(r'login/', views.get_login),
    url(r'login_submit/', views.login_submit, name='login_submit'),
    url(r'logout/', views.logout_view, name='logout')
]
