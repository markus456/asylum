# -*- coding: utf-8 -*-
from creditor.models import RecurringTransaction
from django import forms
from django.conf import settings
from django.utils.functional import keep_lazy
from django.utils.translation import gettext_lazy as _

from .models import MembershipApplication


@keep_lazy(str)
def rules_accepted_proxy(msg):
    return msg % settings.APPLICATION_RULES_URL


class ApplicationForm(forms.ModelForm):
    rules_accepted = forms.BooleanField(required=True, label=rules_accepted_proxy(_("I have read and accept <a href=\"%s\" target=\"_blank\">the rules</a>")))
    required_css_class = 'required'

    class Meta:
        model = MembershipApplication
        fields = [
            'fname',
            'lname',
            'city',
            'email',
            'phone',
            'nick',
        ]


class RTInlineForm(forms.ModelForm):
    amount = forms.DecimalField(max_value=0)

    class Meta:
        model = RecurringTransaction
        fields = [
            'start',
            'end',
            'label',
            'rtype',
            'tag',
        ]
