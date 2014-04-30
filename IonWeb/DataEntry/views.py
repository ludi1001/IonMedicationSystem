from django.shortcuts import render_to_response, render
from django.template import RequestContext
from mongoengine.django.auth import User
from account.models import IonUser
from models import patient
from dispenser.models import dispenser
from helper import RxNorm, helper
from itertools import chain
import datetime
import urllib2
import json
import re

def patientinfo(request):
   message = ""
   if request.method == 'POST':
      if request.POST['requestType'] == 'newPatient':
         firstName = request.POST['firstName']
         lastName = request.POST['lastName']
         birthDate = request.POST['birthDate']
         
         if(helper.validate(birthDate)):
            username = firstName + lastName         
            userNum = len(User.objects(__raw__={'username':{'$regex': '^' + username, '$options' : 'i'}}))

            user = User.create_user(username + str(userNum), 'password')
            user.first_name = firstName
            user.last_name = lastName
            user.save()
            ion_user = IonUser(user=user, group='patient', birthdate=birthDate)
            ion_user.save()
       
            newPatient = patient(firstName=firstName, lastName=lastName, activeMeds = [], user=ion_user)
            newPatient.save()
         else:
            message = "Invalid birth date format. (should be mm-dd-yyyy)"

      if request.POST['requestType'] == 'deletePatient':
         id = request.POST['id']
         patient.objects(id=id)[0].delete()
         # don't know if we actually want to give people the ability to delete medical records...
   return render_to_response('patientinfo.html', {'Patients': patient.objects, 'message': message},
                              context_instance=RequestContext(request))

def update(request):
   id = eval("request." + request.method + "['id']")
   Patient = patient.objects(id=id)[0]

   if request.method == 'POST':
      Patient.name = request.POST['name']
      Patient.editedTime = datetime.datetime.now()
      Patient.dispenserID = request.POST['dispenserID']
      Patient.save()
      template = 'index.html'
      params = {'Patients': patient.objects}

   elif request.method == 'GET':
      template = 'update.html'
      params = {'patient':Patient}

   return render_to_response(template, params, context_instance=RequestContext(request))
   
def medinfo(request):
   if 'requestType' in request.GET:
      if request.GET['requestType'] == 'getNameSuggestions':
         name = request.GET['medName']
         url = ''.join(['http://rxnav.nlm.nih.gov/REST/spellingsuggestions?name=', name])
         nameSuggestions = RxNorm.getJSON(url)
         return render_to_response('medinfo.html', {'nameSuggestions': nameSuggestions}, 
         context_instance=RequestContext(request))
      elif request.GET['requestType'] == 'getMedSuggestions':
         name = request.GET['medName']
         url = ''.join(['http://rxnav.nlm.nih.gov/REST/drugs?name=', name])
         medSuggestions = RxNorm.getJSON(url)
         return render_to_response('medinfo.html', {'medSuggestions': medSuggestions}, 
         context_instance=RequestContext(request))
      elif request.GET['requestType'] == 'getMedicationInfo':
         medID = request.GET['medID']
         url = ''.join(['http://rxnav.nlm.nih.gov/REST/rxcui/', medID])
         attributes = RxNorm.getJSON(''.join([url, '/allProperties?prop=attributes']))
         names = RxNorm.getJSON(''.join([url, '/allProperties?prop=names']))
         ndcs = RxNorm.getJSON(''.join([url, '/ndcs']))
         if ndcs['ndcGroup']['ndcList']:
            ndc = ndcs['ndcGroup']['ndcList']['ndc'][0]
         else:
            ndc = 0
         name = RxNorm.getName(medID);
         # dailymed = RxNorm.getJSON(''.join(['http://dailymed.nlm.nih.gov/dailymed/services/v1/ndc/', ndc, '/imprintdata.json']))
         return render_to_response('medinfo.html', {'attributes': json.dumps(attributes, indent=3), 'names': names, 'ndc': ndc, 'rxuid': medID, 'name' : name}, 
         context_instance=RequestContext(request))
   
   return render_to_response('medinfo.html', {}, context_instance=RequestContext(request))

def users(request):
   return render_to_response("users.html", {}, context_instance=RequestContext(request))
   
def search(request):
   params = {}
   message = ''
   if request.GET.get('requestType') == 'searchPatients':
      searchTerms = re.split('\W+', request.GET.get('search'))
      patientlist = []
      searchlist = []
      
      for searchTerm in searchTerms:
         searchlist.append({'firstName':{'$regex': '^' + searchTerm, '$options' : 'i'}})
         searchlist.append({ 'lastName':{'$regex': '^' + searchTerm, '$options' : 'i'}})
         
      patientlist = list(chain(patientlist, patient.objects(__raw__={ '$or' : searchlist})))
         
      params = { 'patientlist' : patientlist }
      
   if request.GET.get('requestType') == 'patientInfo':
      id = request.GET.get('id')
      Patient = patient.objects(id=id)[0]
      caretakers = IonUser.objects(group__in=["caretaker", "admin"])
      params = {'requestType' : 'patientInfo', 'patient': Patient, 'dispensers': dispenser.objects, 'caretakers': caretakers}
      
      params['rxuid'] = 0
      params['numPills'] = 1
      params['dispensed'] = "checked"
      params['startDate'] = datetime.datetime.now().strftime("%Y-%m-%d")
      params['times'] = "09:00am"
      params['repeatDays'] = 1
      params['repeat'] = "checked"
      params['display'] = 'none'
            
      if request.method == 'POST':
         if request.POST.get('requestType') == 'updateDisp':
            newDispenser = dispenser.objects(id=request.POST.get('newDisp'))[0]
            Patient.dispenser = newDispenser
            Patient.save()
         
         if request.POST.get('requestType') == 'updateCaretaker':
            newCaretaker = IonUser.objects(id=request.POST.get('newCaretaker'))[0]
            Patient.caretaker = newCaretaker
            Patient.save()
         
         if request.POST.get('requestType') == 'deactivateMed':
            rxuid = request.POST['rxuid']
            for index, medication in enumerate(Patient.medications):
               if medication['rxuid'] == rxuid:
                  medication['active'] = False
                  medication['deactivated'] = datetime.datetime.now()
            Patient.save()
            
            params['rxuid'] = medication['rxuid']
            params['numPills'] = medication['quantity']
            params['dispensed'] = "checked" if medication['dispensed'] else ""
            params['startDate'] = medication['startDate']
            params['times'] = medication['times'][0]
            params['repeatDays'] = medication['repeatDays']
            params['repeat'] = "checked" if medication['repeatDays'] > -1 else ""
            params['display'] = 'block'
            
         if request.POST['requestType'] == 'addMedication':
            rxuid = request.POST['rxuid']
            quantity = request.POST['numPills'] 
            dispensed = 'dispensable' in request.POST
            startDate = request.POST['startDate']
            times = request.POST.getlist('times')
            repeat = 'repeat' in request.POST
            repeatDays = request.POST.get('repeatDays', -1)
   
            rxuidRepeat = False
            
            for medication in Patient.medications:
               if medication['rxuid'] == rxuid and medication['active'] == True:
                  rxuidRepeat = True
                  
            if not repeat:
               repeatDays = -1
            
            if rxuid == "":
               message = "Error: Please enter a rxuid"
               rxuid = 0
            elif quantity == "":
               message = "Error: Please enter an quantity"
               quantity = 1
            elif RxNorm.getName(rxuid) == None:
               message = "Error: Invalid rxuid"
            elif rxuidRepeat:
               message = "Patient already has an entry for this medication"
            elif int(quantity) < 0 or int(quantity) > 50:
               message = 'Error: Quantity must be between 0 and 50'
            elif not helper.validate(startDate): 
               message = 'Error: Medication start date must be mm-dd-yyy'
               startDate = datetime.datetime.now().strftime("%Y-%m-%d")
            elif datetime.datetime.strptime(startDate, "%Y-%m-%d").date() < datetime.date.today():
               message = 'Error: Start date can not be in the past'
            elif len(times) == 0:
               message = 'Error: No medication times specified'
               times.append("09:00am")
            elif repeat and repeatDays == "":
               message = 'Error: Repeat every how many days?'
               repeatDays = 1
            else:
               Patient.medications.append({'rxuid': rxuid, 'quantity': quantity, 'dispensed': dispensed, 'startDate': startDate, 'times': times, 'repeatDays': repeatDays, 'active': True})
               Patient.save()
            
            params['rxuid'] = rxuid
            params['numPills'] = quantity
            params['dispensed'] = "checked" if dispensed else ""
            params['startDate'] = startDate
            params['times'] = times[0]
            params['repeatDays'] = repeatDays
            params['repeat'] = "checked" if repeat else ""
            params['display'] = 'block'
   params['message'] = message
   
   return render(request, "search.html", params)
