from mongoengine import *
import re

class HashField(StringField):
    """Represents SHA-2 hash output"""
    
    HASH_REGEX = re.compile(r"^[0-9a-f]{40}")
    
    def validate(self, value):
        if not HashField.HASH_REGEX.match(value):
            raise ValidationError("Not a valid SHA-2 hash: %s".format(value))

class User(Document):
    """Represents a user in the system"""
    username = StringField(max_length=120, required=True)
    password = HashField()
    user_type = StringField()
