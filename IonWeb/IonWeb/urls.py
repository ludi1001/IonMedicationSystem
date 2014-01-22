from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'DataEntry.views.index'),
    url(r'^medinfo/', 'DataEntry.views.medinfo'),
    url(r'^update/', 'DataEntry.views.update'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^account/login', 'account.views.login'),
    url(r'^account/create', 'account.views.create'),
    url(r'^account/test','account.views.test'),
    url(r'^account/restricted','account.views.restricted'),
    url(r'^account/logout','account.views.logout')
)
