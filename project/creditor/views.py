# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import ListView
from creditor.models import Transaction, TransactionTag
from django.db.models import Sum, Count
from django.utils import timezone


class TransactionMonthView(ListView):
   model = Transaction
   template_name = "admin/table.html"
   
   param_tag = None
   def get_queryset(self):

      self.param_year = self.kwargs['year']
      self.param_month = self.kwargs['month']

      if('tag' in self.kwargs and int(self.kwargs['tag']) in TransactionTag.objects.values_list('pk', flat=True)):
         self.param_tag = TransactionTag.objects.filter(pk=int(self.kwargs['tag']))[0]
         return Transaction.objects.filter(stamp__year=self.param_year).filter(stamp__month=self.param_month).filter(tag__pk=self.param_tag.pk).order_by('owner__lname','owner__fname')
      
      return Transaction.objects.filter(stamp__year=self.param_year).filter(stamp__month=self.param_month).order_by('owner__lname','owner__fname')
   
   
   def get_context_data(self, **kwargs):
      context = super(TransactionMonthView, self).get_context_data(**kwargs)
      context['income'] = self.get_queryset().filter(amount__gte=0).aggregate(sum=Sum('amount'))
      context['receivables'] = self.get_queryset().filter(amount__lt=0).aggregate(sum=Sum('amount'))
      context['freq_table'] = self.get_queryset().values('amount').annotate(freq=Count('amount')).order_by('-amount')
      context['total'] = self.get_queryset().aggregate(sum=Sum('amount'))
      context['year'] = self.param_year
      context['tag'] = self.param_tag
      context['tag_pk'] = "" if self.param_tag == None else self.param_tag.pk
      context['month'] = self.param_month.rjust(2, "0")
      context['months'] = ['01','02','03','04','05','06','07','08','09','10','11','12']
      context['years'] = [str(d.year) for d in Transaction.objects.datetimes('stamp', 'year')]
      context['tags'] = TransactionTag.objects.values('pk','label').order_by('pk')
      
      return context

class TransactionYearView(ListView):
   model = Transaction
   template_name = "admin/table_year.html"
   
   param_year = timezone.now().year
   param_tag = None
   def get_queryset(self):
      
      if('year' in self.kwargs):
         self.param_year = self.kwargs['year']
       
      # tag number must refer to existing TransactionTag
      if('tag' in self.kwargs and int(self.kwargs['tag']) in TransactionTag.objects.values_list('pk', flat=True)):
         self.param_tag = TransactionTag.objects.filter(pk=int(self.kwargs['tag']))[0]
         return Transaction.objects.filter(stamp__year=self.param_year).filter(tag__pk=self.param_tag.pk)
      
      return Transaction.objects.filter(stamp__year=self.param_year)
   
   
   def get_context_data(self, **kwargs):
      context = super(TransactionYearView, self).get_context_data(**kwargs)
      context['receivables'] = self.get_queryset().filter(amount__lt=0).extra(select={'month': "to_char(stamp, 'MM' )"}).values('month').annotate(sum=Sum('amount')).order_by()
      context['income'] = self.get_queryset().filter(amount__gte=0).extra(select={'month': "to_char(stamp, 'MM' )"}).values('month').annotate(sum=Sum('amount')).order_by()
      context['total'] = self.get_queryset().extra(select={'month': "to_char(stamp, 'MM' )"}).values('month').annotate(sum=Sum('amount')).order_by()
      context['tag'] = self.param_tag
      context['tag_pk'] = "" if self.param_tag == None else self.param_tag.pk
      context['year'] = self.param_year
      context['months'] = ['01','02','03','04','05','06','07','08','09','10','11','12']
      context['years'] = [d.year for d in Transaction.objects.datetimes('stamp', 'year')]
      context['tags'] = TransactionTag.objects.values('pk','label').order_by('pk')
      
      return context

