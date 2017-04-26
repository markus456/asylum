# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.views import generic

from .forms import GrantRequestForm
from .models import GrantRequest, GrantType
from members.models import Member


class ApplyView(generic.FormView):
    template_name = "active_members/application_form.html"
    form_class = GrantRequestForm

    def form_valid(self, form):
        request = GrantRequest()
        request.requestor = Member.objects.get(email=form.cleaned_data["your_email"])
        request.requested_grant = GrantType.objects.get(grant_type=form.cleaned_data["requested_grant"])
        request.save()
        return super(ApplyView, self).form_valid(form)

    def get_success_url(self):
        return reverse('active-members-application_received')

class ApplicationReceivedView(generic.TemplateView):
    template_name = "active_members/application_received.html"


class HomeView(generic.base.RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        return reverse('active-members-apply')
