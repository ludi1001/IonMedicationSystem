from django.conf.urls import include, patterns, url

urlpatterns = patterns('dispenser.views',
    url(r'^$', 'management'),
    url(r'^view$','dispenser_view'),
    url(r'^admin$','dispenser_admin'),
    url(r'^loadcompartment$','load_compartment'),
    url(r'^dispense-medication$', 'dispense_medication'),
    url(r'^take-medication$', 'take_medication'),
    url(r'^decrement-pills$', 'decrement_pills'),
    url(r'^manage/remove-compartment$', 'remove_compartment_ajax')
)