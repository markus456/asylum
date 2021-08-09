from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()

@register.filter(name='month_sum_value')
def month_sum_value(month_array, month):
    for d in month_array:
      if str(month) == d['month']:
         return d['sum']
    return None


@register.filter(name='create_tag_param')
def create_tag_param(tagnumber):
    if tagnumber is None or tagnumber == "":
        return ""
    elif int(tagnumber) > 0:  # skip this param if there is none
        return "/tag=" + str(tagnumber)
    return ""

@register.filter(name='eur')
def eur(numval):
    if numval is None:
        return "."
    return intcomma(numval)+" €"
