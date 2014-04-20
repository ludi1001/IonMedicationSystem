from mongoengine import *
import datetime

class notification(Document):
  generator = StringField(required=True)
  creation_date = DateTimeField()
  modified_date = DateTimeField()
  
  target =  ReferenceField('IonUser', required=True)
  viewed_date = DateTimeField(default=None) #when notification was seen by user (or dismissed)
  retrieval_date = DateTimeField(default=None) #when the user agent retrieved the notification (but the user may not have seen it
  type = StringField()
  
  meta = {'allow_inheritance': True}
  
  def save(self, *args, **kwargs):
    if not self.creation_date:
        self.creation_date = datetime.datetime.now()
    self.modified_date = datetime.datetime.now()
    return super(notification, self).save(*args, **kwargs)

  def mark_read(self):
    self.viewed_date = datetime.datetime.now()
    self.save()
    
  def mark_retrieved(self):
    if not self.retrieval_date:
      self.retrieval_date = datetime.datetime.now()
    self.save()
  
