from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
   url(r'^$', 'mongobacked.DataEntry.views.index'),
   url(r'^medinfo/', 'mongobacked.DataEntry.views.medinfo'),
   url(r'^update/', 'mongobacked.DataEntry.views.update'),
   url(r'^admin/', include(admin.site.urls)),
)
