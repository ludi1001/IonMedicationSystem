from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'DataEntry.views.index'),
    url(r'^medinfo/', 'DataEntry.views.medinfo'),
    url(r'^update/', 'DataEntry.views.update'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^account/', include('account.urls'))
)
