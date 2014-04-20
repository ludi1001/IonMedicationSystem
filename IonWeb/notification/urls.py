from django.conf.urls import include, patterns, url

urlpatterns = patterns('notification.views',
    url(r'^$', 'list_all_notifications'),
    url(r'^get$','get_notifications'),
    url(r'^medStatus$','medication_status'),
    url(r'^read$','mark_notification_read'),
    url(r'^pack/check$', 'pack_check'),
    url(r'^pack/confirm$','pack_confirm')
)