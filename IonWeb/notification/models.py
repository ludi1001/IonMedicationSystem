from mongoengine import *
import datetime

class notification(Document):
  generator = StringField(required=True)
  modified_date = DateTimeField()
  
  target =  ReferenceField('IonUser', required=True)
  viewed_date = DateTimeField()
  type = StringField()
  
  meta = {'allow_inheritance': True}
  
  def clean(self):
    self.modified_date = datetime.datetime.now()

  def mark_read(self):
    self.viewed_date = datetime.datetime.now()
  
