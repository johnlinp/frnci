from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'landing.views.home', name='home'),
    url(r'^locals$', 'landing.views.locals', name='locals'),

    url(r'^admin/', include(admin.site.urls)),
)
