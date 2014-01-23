from django.shortcuts import render
from django.http import HttpResponse

from mongoengine import django
import mongoengine.django.mongo_auth.models
from mongoengine.django.auth import User

from django.contrib.auth import authenticate
import django.contrib.auth as auth
from django.contrib.auth.decorators import login_required

from models import IonUser

def create(request):
    user = User.create_user('j', 'password', 'lennon@thebeatles.com')
    user.groups = ['patient']
    user.save()
    ion_user = IonUser(user=user, group='patient')
    ion_user.save()
    return HttpResponse("Account create successful")
    
def login(request):
    user = authenticate(username='j', password='password')
    auth.login(request, user)
    if user is None:
        return HttpResponse("Login failed")
    else:
        return HttpResponse("Login successful: " + IonUser.objects(user=user)[0].group)
        
@login_required
def restricted(request):
    return HttpResponse("Hai")

@login_required
def test(request):
    return HttpResponse("Bai")

def logout(request):
    """
    try:
        del request.session['user_id']
        del request.session['user_type']
    except:
        pass
    """
    auth.logout(request)
    return HttpResponse("Logout")
    return HttpResponse("Logged out")
