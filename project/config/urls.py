# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import access.rest
import creditor.rest
import members.rest
from django.conf import settings
from django.urls import re_path
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.views import defaults as default_views
from django.views.generic import TemplateView
from rest_framework import routers
from rest_framework.authtoken import views as authtoken_views

router = routers.DefaultRouter()
router.register(r'members/types',        members.rest.MemberTypeViewSet)
router.register(r'members/tags',         members.rest.MembershipApplicationTagViewSet)
router.register(r'members/applications', members.rest.MembershipApplicationSerializerViewSet)
router.register(r'members',              members.rest.MemberViewSet)
router.register(r'creditor/transactions/recurring', creditor.rest.RecurringTransactionViewSet)
router.register(r'creditor/transactions',           creditor.rest.TransactionViewSet)
router.register(r'creditor/tags',                   creditor.rest.TransactionTagViewSet)
router.register(r'access/tokens/types', access.rest.TokenTypeViewSet)
router.register(r'access/tokens',       access.rest.TokenViewSet)
router.register(r'access/types',        access.rest.AccessTypeViewSet)
router.register(r'access/grants',       access.rest.GrantViewSet)


urlpatterns = [
    re_path(r'^$', TemplateView.as_view(template_name='pages/home.html'), name="home"),
    re_path(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name="about"),

    # Django Admin, use {% url 'admin:index' %}
    re_path(settings.ADMIN_URL, admin.site.urls),

    # Your stuff: custom urls includes go here
    re_path(r'^members/', include('members.urls')),
    re_path(r'^velkoja/', include('velkoja.urls')),

    re_path(r'^api/', include(router.urls)),
    re_path(r'^api/members/sinlist', members.rest.MemberSinView.as_view()),
    re_path(r'^api-auth/get-token/', authtoken_views.obtain_auth_token),
    re_path(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    re_path('^markdownx/', include('markdownx.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        re_path(r'^400/$', default_views.bad_request),
        re_path(r'^403/$', default_views.permission_denied),
        re_path(r'^404/$', default_views.page_not_found),
        re_path(r'^500/$', default_views.server_error),
    ]

    # This is required by Django Debug Toolbar
    import debug_toolbar
    urlpatterns += [
        re_path(r'^__debug__/', include(debug_toolbar.urls)),
    ]
