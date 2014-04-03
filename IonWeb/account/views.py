from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.contrib.auth import authenticate
import django.contrib.auth as auth
import mongoengine.django.mongo_auth.models
from mongoengine.django.auth import User
from mongoengine import django
import datetime

from models import IonUser
from privilege_tests import is_in_group

def index(request):
   return render_to_response('index.html', {},
      context_instance=RequestContext(request))

def get_info(request):
  ion_user = IonUser.objects(user=request.user)[0]
  return HttpResponse(ion_user.id)
      
#@is_in_group('admin')      
def create(request):
    user = User.create_user('iveel', 'password', 'solix@trewq.com')
    #user.groups = ['patient']
    user.save()
    ion_user = IonUser(user=user, group='admin', birthdate=datetime.datetime.now())
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
        
@is_in_group(['caretaker', 'admin'])
def restricted(request):
    return HttpResponse("Hai")

@is_in_group('patient')
def test(request):
    return HttpResponse("Bai")

def logout(request):
    auth.logout(request)
    return HttpResponse("Logged out")
