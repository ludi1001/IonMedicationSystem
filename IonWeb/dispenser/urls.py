from django.conf.urls import include, patterns, url

urlpatterns = patterns('dispenser.views',
    url(r'^$', 'management'),
    url(r'^view$','dispenser_view'),
)