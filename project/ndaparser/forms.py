# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import gettext_lazy as _


class UploadForm(forms.Form):
    ndafile = forms.FileField(required=False, label=_("Transactions file"))
    csvfile = forms.FileField(required=False, label=_("Transactions CSV file"))
