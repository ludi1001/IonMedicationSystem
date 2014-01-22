from mongoengine import *
import re

#connect(DBNAME)

class Sha256HashField(StringField):
    """Represents SHA-2 hash output"""
    
    HASH_REGEX = re.compile(r"^[0-9a-f]{64}")
    
    def validate(self, value):
        if not HashField.HASH_REGEX.match(value):
            raise ValidationError("Not a valid SHA-256 hash: %s".format(value))

class User(Document):
    """Represents a user in the system"""
    username = StringField(max_length=120, required=True)
    password = Sha256HashField(required=True)
    user_type = StringField(required=True)
    
import mongoengine.django.mongo_auth.models
import mongoengine.django.auth as auth
class BetterUser(auth.User):
    group = StringField()
