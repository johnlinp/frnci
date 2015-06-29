from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'landing.views.home', name='home'),
    url(r'^locals/area/(?P<area_str>.*)/$', 'landing.views.locals_area', name='locals-area'),
    url(r'^locals/interest/(?P<interest_str>.*)/$', 'landing.views.locals_interest', name='locals-interest'),

    url(r'^pilot/$', 'landing.views.pilot', name='pilot'),

    url(r'^fa$', 'landing.views.fa'),

    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
    url(r'^accounts/', include('allaccess.urls')),

    url(r'^admin/locals/manage/$', 'landing.views.locals_manage', name='locals-manage'),
    url(r'^admin/locals/import/$', 'landing.views.locals_import', name='locals-import'),
    url(r'^admin/', include(admin.site.urls)),
)
