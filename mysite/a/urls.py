from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^preadd/$', views.preadd, name='home'),
    url(r'^add/(\d+)/(\d+)/$', views.add, name='add'),
]
