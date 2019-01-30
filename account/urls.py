from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^login$', views.get_login, name='login'),
    url(r'^home$', views.get_home, name='home'),
    url(r'^', views.account, name='accounts'),
]
