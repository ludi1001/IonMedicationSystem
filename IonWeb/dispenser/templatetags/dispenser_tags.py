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
