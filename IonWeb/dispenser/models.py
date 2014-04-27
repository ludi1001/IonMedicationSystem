from mongoengine import *

class dispenser(Document):
   user = ReferenceField('IonUser', required=True)
   location = StringField(max_length=120, required=True)
   slots = ListField()
   
class compartment(Document):
   rxuid = IntField()
   lot = IntField();
   quantity = IntField();
   expiration = DateTimeField();
   rfid = StringField();
   loaded = BooleanField()
