from django.conf.urls import patterns, include, url 
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'account.views.index'),
    url(r'^patientinfo$', 'DataEntry.views.patientinfo'),
    url(r'^medinfo$', 'DataEntry.views.medinfo'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^account/', include('account.urls')),
    url(r'^notification/',include('notification.urls')),
    url(r'^dispenser/', include('dispenser.urls')),
    url(r'^compartment$', 'dispenser.views.compartments'),
    url(r'^loadcompartment$', 'dispenser.views.loadcompartment'),
    url(r'^updatecompartment$', 'dispenser.views.updatecompartment'),
    url(r'^notifications$', 'notification.views.notifications'),
    url(r'^medication$', 'notification.views.medication'),
    url(r'^rfid$', 'dispenser.views.updateRFID'),  
    url(r'^search$', 'DataEntry.views.search'),    
    url(r'^users$', 'DataEntry.views.users'),
    url(r'^dispense-medication$', 'django.shortcuts.render', {'template_name': 'dispense_medication.html'})
) 
urlpatterns += staticfiles_urlpatterns()

