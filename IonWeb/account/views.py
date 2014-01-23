from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.contrib.auth import authenticate
import django.contrib.auth as auth

from mongoengine import django
import mongoengine.django.mongo_auth.models
from mongoengine.django.auth import User

from models import IonUser
from privilege_tests import is_in_group

def create(request):
    user = User.create_user('j', 'password', 'lennon@thebeatles.com')
    user.groups = ['patient']
    user.save()
    ion_user = IonUser(user=user, group='patient')
    ion_user.save()
    return HttpResponse("Account create successful")
    
def login(request):
    params = {}
    if request.method == 'POST':
        if 'username' in request.POST and 'password' in request.POST:
            #attempt authentication
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            auth.login(request, user)
            if user is None:
                return HttpResponse("Login failed")
            else:
                return HttpResponse("Login successful: " + IonUser.objects(user=user)[0].group)
        else:
            if 'username' not in request.POST:
                params['message'] = "Missing username"
            else:
                params['message'] = "Missing password"
    return render_to_response('login.html', params, context_instance=RequestContext(request))
        
@is_in_group('caretaker')
def restricted(request):
    return HttpResponse("Hai")

@is_in_group('patient')
def test(request):
    return HttpResponse("Bai")

def logout(request):
    auth.logout(request)
    return HttpResponse("Logged out")
