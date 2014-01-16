from django.shortcuts import render_to_response
from django.template import RequestContext
from models import patient
import datetime
import urllib2
import json

# a lot of this was taken from a sample 'blongo' project
def index(request):
   if request.method == 'POST':
      if request.POST['requestType'] == 'newPatient':
         name = request.POST['name']
         newPatient = patient(name=name)
         newPatient.creationTime = datetime.datetime.now()
         newPatient.save()

      if request.POST['requestType'] == 'deletePatient':
         id = request.POST['id'] #TEST THIS eval("request." + request.method + "['id']")
         patient.objects(id=id)[0].delete()
         # don't know if we actually want to give people the ability to delete medical records...

   return render_to_response('index.html', {'Patients': patient.objects},
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
         nameSuggestions = getJSON(url)
         return render_to_response('medinfo.html', {'nameSuggestions': nameSuggestions}, 
         context_instance=RequestContext(request))
      elif request.GET['requestType'] == 'getMedSuggestions':
         name = request.GET['medName']
         url = ''.join(['http://rxnav.nlm.nih.gov/REST/drugs?name=', name])
         medSuggestions = getJSON(url)
         return render_to_response('medinfo.html', {'medSuggestions': medSuggestions}, 
         context_instance=RequestContext(request))
      elif request.GET['requestType'] == 'getMedicationInfo':
         medID = request.GET['medID']
         url = ''.join(['http://rxnav.nlm.nih.gov/REST/rxcui/', medID])
         attributes = getJSON(''.join([url, '/allProperties?prop=attributes']))
         names = getJSON(''.join([url, '/allProperties?prop=names']))
         ndcs = getJSON(''.join([url, '/ndcs']))
         ndc = ndcs['ndcGroup']['ndcList']['ndc'][0]
         # dailymed = getJSON(''.join(['http://dailymed.nlm.nih.gov/dailymed/services/v1/ndc/', ndc, '/imprintdata.json']))
         return render_to_response('medinfo.html', {'attributes': json.dumps(attributes, indent=3), 'names': names, 'ndc': ndc}, 
         context_instance=RequestContext(request))
   
   return render_to_response('medinfo.html', {}, context_instance=RequestContext(request))
                              
def getJSON(url):
   req = urllib2.Request(url, None, {'Accept': 'application/json'})
   response = urllib2.urlopen(req)
   ret = json.loads(response.read(), 'utf-8')
   response.close()
   return ret
