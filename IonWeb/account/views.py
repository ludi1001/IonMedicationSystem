from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import RequestContext
from django.contrib.auth import authenticate
import django.contrib.auth as auth
import mongoengine.django.mongo_auth.models
from mongoengine.django.auth import User
from helper import helper
from DataEntry.models import patient
from mongoengine import django
import datetime

from models import IonUser
from dispenser.models import dispenser
from privilege_tests import is_in_group, ALL
from shortcuts import choose_group_dependent_page, get_ion_user

@is_in_group(ALL)
def index(request):
  def index_patient(request, user):
   params = {}
   message = ""
   
   IonUser = helper.get_ion_user(request)
   if patient.objects(user=IonUser):
      Patient = patient.objects(user=IonUser)[0]
      params['patient'] = Patient
   else:
      message = "Not a patient"
   params['message'] = message
   
   return render(request, "patient_home.html", params)

  def index_dispenser(request, user):
    user = get_ion_user(request)
    disp = dispenser.objects(user=user)[0]
    return render(request, 'dispenser_home.html', {'dispenser': disp})
  def index_caretaker(request, user):
    return render(request, 'index.html')
  def index_admin(request, user):
    return render(request, 'index.html')
  return choose_group_dependent_page(request, patient=index_patient,dispenser=index_dispenser,caretaker=index_caretaker,admin=index_admin)
      
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
  #from dispenser.models import dispenser, compartment
  #dispenser.objects().delete()
  #compartment.objects().delete()
  #from notification.models import notification
  #notification.objects().delete()
  return HttpResponse("authenticated: {0}".format(request.user.is_authenticated()))
  
@is_in_group(ALL)    
def logout(request):
  auth.logout(request)
  return HttpResponse("Logged out")
