from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'mongobacked.DataEntry.views.index'),
    url(r'^update/', 'mongobacked.DataEntry.views.update'),
    url(r'^delete/', 'mongobacked.DataEntry.views.delete'),
    url(r'^admin/', include(admin.site.urls)),
)
