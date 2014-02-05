from django import template
from ..models import compartment

register = template.Library()

@register.filter(name='get_compartment')
def get_compartment(id):
   comp = compartment.objects(id=id)[0]
   return comp