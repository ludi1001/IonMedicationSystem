from mongoengine import *

class dispenser(Document):
   location = StringField(max_length=120, required=True)
   slots = ListField(required=True)

class compartment(Document):
   rxuid = IntField()
   lot = IntField();
   quantity = IntField();
   expiration = DateTimeField();
   rfid = StringField();
