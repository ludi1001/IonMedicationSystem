from mongoengine import *

class patient(Document):
   firstName = StringField(max_length=120, required=True)
   lastName = StringField(max_length=120, required=True)
   medications = ListField()
   dispenser = ReferenceField('dispenser')
   editedTime = DateTimeField()
   user = ReferenceField('IonUser', required=True) # required = True
   medHistory = ListField();
   activeMeds = ListField();
   caretaker = ReferenceField('IonUser')
  
  