from mongoengine import *

class IonUser(Document):
    user = ReferenceField('User', reverse_delete_rule=CASCADE)
    group = StringField(r'patient|caretaker|admin|dispenser', required=True)
    birthdate = DateTimeField(required=True)