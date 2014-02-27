from django.conf.urls import include, patterns, url

urlpatterns = patterns('notification.views',
    url(r'^test$','generate_notification'),
)