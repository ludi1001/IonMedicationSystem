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
from privilege_tests import is_in_group, ALL

@is_in_group(ALL)
def index(request):
  return render_to_response('index.html', {},
    context_instance=RequestContext(request))
      
@is_in_group('admin')      
def create(request):
  user = User.create_user('dispenser', 'password', 'solix@trewq.com')
  #user.groups = ['patient']
  user.save()
  ion_user = IonUser(user=user, group='dispenser', birthdate=datetime.datetime.now())
  ion_user.save()
  return HttpResponse("Account create successful")

@is_in_group(ALL)
def profile(request):
  user = IonUser.objects(user=request.user)[0]
  return render_to_response('profile.html', {'user':user},context_instance=RequestContext(request))
  
def temp(request):
  return HttpResponse("authenticated: {0}".format(request.user.is_authenticated()))
  
@is_in_group(ALL)    
def logout(request):
  auth.logout(request)
  return HttpResponse("Logged out")
