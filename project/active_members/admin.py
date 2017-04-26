# -*- coding: utf-8 -*-
import itertools

from access.models import AccessType, Grant, Token
from creditor.models import RecurringTransaction
from django import forms
from django.contrib import admin
from django.db import models
from django.utils.functional import allow_lazy, lazy
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from reversion.admin import VersionAdmin

from .models import GrantType
from .models import GrantRequest

class GrantTypeAdmin(VersionAdmin):
    list_display = (
        'grant_type',
    )
    search_fields = ['grant_type']
    ordering = ['grant_type']

class GrantRequestAdmin(VersionAdmin):
    list_display = (
        'notes',
        'received',
        'requestor',
        'requested_grant'
    )
    search_fields = ['requestor']
    ordering = ['received']

# Register your models here.
admin.site.register(GrantType, GrantTypeAdmin)
admin.site.register(GrantRequest, GrantRequestAdmin)
