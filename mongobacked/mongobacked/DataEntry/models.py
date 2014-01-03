from mongoengine import *
from mongobacked.settings import DBNAME

connect(DBNAME)

class patient(Document):
   name = StringField(max_length=120, required=True)
   medications = DictField()
   dispenserID = StringField(max_length=100)
   creationTime = DateTimeField(required=True)
   editedTime = DateTimeField()
   dispensed = BooleanField()