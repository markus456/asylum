# -*- coding: utf-8 -*-
from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.HomeView.as_view(), name="members-home"),
    re_path(r'^apply/?$', views.ApplyView.as_view(), name="members-apply"),
    re_path(r'^apply/done/?$', views.ApplicationReceivedView.as_view(), name="members-application_received"),
]
