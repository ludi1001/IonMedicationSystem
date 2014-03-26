from django.conf.urls import include, patterns, url

urlpatterns = patterns('',
    url(r'^login/?', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^create$', 'account.views.create'),
    url(r'^test$','account.views.test'),
    url(r'^restricted$','account.views.restricted'),
    url(r'^logout$','django.contrib.auth.views.logout_then_login')
)