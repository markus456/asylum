# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.utils.functional import allow_lazy, lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.core.exceptions import ObjectDoesNotExist
from members.models import Member

from .models import GrantRequest, GrantType

class GrantRequestForm(forms.Form):
    your_email = forms.EmailField(label = "Email")
    requested_grant = forms.ModelChoiceField(queryset = GrantType.objects.all(), label = "Requested Grant", empty_label = None)

    def clean(self):
        cleaned_data = super(GrantRequestForm, self).clean()
        email = cleaned_data["your_email"]

        try:
            Member.objects.get(email=email)
        except ObjectDoesNotExist:
            raise forms.ValidationError("Email not found.")

