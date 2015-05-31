from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'landing.views.home', name='home'),
    url(r'^locals/area/(?P<area>.*)/$', 'landing.views.locals_area', name='locals-area'),
    url(r'^locals/interest/(?P<interest>.*)/$', 'landing.views.locals_interest', name='locals-interest'),
    url(r'^locals/manage/$', 'landing.views.locals_manage', name='locals-manage'),
    url(r'^locals/import/$', 'landing.views.locals_import', name='locals-import'),

    url(r'^admin/', include(admin.site.urls)),
)
