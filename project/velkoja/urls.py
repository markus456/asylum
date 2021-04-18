# -*- coding: utf-8 -*-
from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^preview/holvi/?$', views.HolviEmailPreviewView.as_view(), name="velkoja-holvi_email_preview"),
    re_path(r'^preview/nordea/?$', views.NordeaEmailPreviewView.as_view(), name="velkoja-nordea_email_preview"),
]
