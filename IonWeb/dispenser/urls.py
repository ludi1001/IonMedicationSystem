from django.conf.urls import include, patterns, url

urlpatterns = patterns('dispenser.views',
    url(r'^$', 'management'),
    url(r'^view$','dispenser_view'),
    url(r'^admin$','dispenser_admin'),
    url(r'^loadcompartment$','load_compartment'),
    url(r'^dispense-medication$', 'dispense_medication')
)