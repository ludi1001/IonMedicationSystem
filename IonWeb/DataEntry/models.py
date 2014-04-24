from mongoengine import *

class patient(Document):
   firstName = StringField(max_length=120, required=True)
   lastName = StringField(max_length=120, required=True)
   medications = ListField()
   dispenserID = StringField(max_length=100)
   editedTime = DateTimeField()
   user = ReferenceField('IonUser', required=True) # required = True
   medHistory = ListField();
   activeMeds = ListField();
   caretaker = ReferenceField('IonUser')
  
  