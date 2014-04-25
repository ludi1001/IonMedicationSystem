from django.conf.urls import include, patterns, url

urlpatterns = patterns('',
    url(r'^login/?', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^$', 'account.views.profile'),
    url(r'^logout$','django.contrib.auth.views.logout_then_login'),
    url(r'^edit$', 'account.views.edit'),
    url(r'^password$', 'django.contrib.auth.views.password_change', {'template_name': 'password_reset.html', 'post_change_redirect':'/account/password-changed'}),
    url(r'^password-changed$', 'django.contrib.auth.views.password_change_done', {'template_name': 'password_change_done.html'}),
    
    url(r'^temp$','account.views.temp')
)