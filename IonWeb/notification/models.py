from mongoengine import *
import datetime

class notification(Document):
  generator = StringField(required=True)
  creation_date = DateTimeField
  modified_date = DateTimeField()
  
  target =  ReferenceField('IonUser', required=True)
  viewed_date = DateTimeField()
  type = StringField()
  
  meta = {'allow_inheritance': True}
  
  def clean(self):
    if not self.creation_date:
      self.creation_date = datetime.datetime.now()
    self.modified_date = datetime.datetime.now()

  
