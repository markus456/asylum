# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name="active-members-home"),
    url(r'^apply/?$', views.ApplyView.as_view(), name="active-members-apply"),
    url(r'^apply/done/?$', views.ApplicationReceivedView.as_view(), name="active-members-application_received"),
]
