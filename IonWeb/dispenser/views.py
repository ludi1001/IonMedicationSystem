from django.shortcuts import render_to_response
from django.template import RequestContext
import datetime
from models import dispenser
from models import compartment

def management(request):
   if request.method == 'POST':
      if request.POST['requestType'] == 'newDispenser':
         location = request.POST['location']
         newDispenser = dispenser(location=location)
         newDispenser.creationTime = datetime.datetime.now()
         newDispenser.slots = [ "" for i in range(int(request.POST['numSlots']))];
         newDispenser.save()
      if request.POST['requestType'] == 'deleteDispenser':
         id = request.POST['id']
         dispenser.objects(id=id)[0].delete()
   return render_to_response('dispenser.html', {'dispensers': dispenser.objects}, context_instance=RequestContext(request))

def compartments(request):
   newID = ""
   if request.method == 'POST':
      if request.POST['requestType'] == 'newCompartment':
         newCompartment = compartment()
         newCompartment.save()
         newID = newCompartment.id
      if request.POST['requestType'] == 'updateCompartment':
         toEdit = compartment.objects(id=request.POST['id'])[0]
         toEdit.rxuid = int(request.POST['rxuid'])
         toEdit.lot = int(request.POST['lot'])
         toEdit.expiration = request.POST['expiration']
         toEdit.save()
      if request.POST['requestType'] == 'deleteCompartment':
         id = request.POST['id']
         compartment.objects(id=id)[0].delete()

   return render_to_response('compartment.html', {'newID': newID}, context_instance=RequestContext(request))

def loadcompartment(request):
   if request.method == 'POST':
      dispID = request.POST['dispID']
      compID = request.POST['compID']
      slotNum = int(request.POST['slotNum'])
      disp = dispenser.objects(id=dispID)[0]
      disp.slots[slotNum] = compID
      disp.save()

   return render_to_response('loadcompartment.html', {}, context_instance=RequestContext(request))
