from django import template
from ..models import compartment
from helper import RxNorm

register = template.Library()

@register.filter(name='get_compartment')
def get_compartment(id):
   comp = compartment.objects(id=id)[0]
   return comp
   
@register.filter(name='get_medName')
def get_medName(rxuid):
   name = RxNorm.getName(rxuid)
   return name

@register.filter(name='get_range')
def get_range(i):
   return range(i)
   
@register.filter(name='last_entries')
def last_entries(queryset, entries):
   index = int(entries) * -1
   return queryset[index:]
   