from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import AnonymousUser
from models import IonUser

#constants
CARETAKER = 'caretaker'
PATIENT = 'patient'
ADMIN = 'admin'
DISPENSER = 'dispenser'
ALL = [CARETAKER, PATIENT, ADMIN, DISPENSER]

def is_in_group(group):
    def test_membership(user):
      if not user.is_authenticated():
          return False
      ion_user = IonUser.objects(user=user)
      if ion_user.count() != 1: #corrupt database, deny access
          return False
      return ion_user[0].group == group or ion_user[0].group in group
    return user_passes_test(test_membership)
	
