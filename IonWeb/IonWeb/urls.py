from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'account.views.index'),
    url(r'^patientinfo/', 'DataEntry.views.patientinfo'),
    url(r'^medinfo/', 'DataEntry.views.medinfo'),
    url(r'^update/', 'DataEntry.views.update'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^account/', include('account.urls')),
    url(r'^dispenser/', 'dispenser.views.management'),
    url(r'^compartment/', 'dispenser.views.compartments'),
    url(r'^loadcompartment', 'dispenser.views.loadcompartment'),
    url(r'^updatecompartment', 'dispenser.views.updatecompartment')
)
