# -*- coding: utf-8 -*-
import random
from decimal import Decimal

from access.models import AccessType
from access.utils import resolve_acl
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_markdown.models import MarkdownField
from reversion import revisions

from asylum.models import AsylumModel
from .handlers import call_saves

class GrantType(AsylumModel):
    label = "Grant Type"
    grant_type = models.CharField(_("Grant Type"), max_length=200, blank=False)

    def __str__(self):
        return self.grant_type

    class Meta:
        verbose_name = _('Grant Type')
        verbose_name_plural = _('Grant Types')

revisions.default_revision_manager.register(GrantType)

class RequestCommon(AsylumModel):
    notes = MarkdownField(verbose_name=_("Notes"), blank=True)
    received = models.DateField(default=timezone.now)
    requestor = models.ForeignKey('members.Member', blank=False, verbose_name=_("Member"), related_name='+')

revisions.default_revision_manager.register(RequestCommon)

class GrantRequest(RequestCommon):
    requested_grant = models.ForeignKey(GrantType, related_name='+', verbose_name=_("Requested Grant"))

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Grant Request')
        verbose_name_plural = _('Grant Requests')

revisions.default_revision_manager.register(GrantRequest)
