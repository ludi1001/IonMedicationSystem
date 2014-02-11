import datetime
from helper import RxNorm
from models import dispenser
from models import compartment
from django.template import RequestContext
from django.shortcuts import render_to_response

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
   return render_to_response('dispenser.html', {'dispensers': dispenser.objects, 'compartments': compartment.objects}, context_instance=RequestContext(request))

def compartments(request):
   newID = ""
   if request.method == 'POST':
      if request.POST['requestType'] == 'newCompartment':
         newCompartment = compartment()
         newCompartment.save()
         newID = newCompartment.id
         
    #  if request.POST['requestType'] == 'expiration'
      if request.POST['requestType'] == 'updateCompartment':
         toEdit = compartment.objects(id=request.POST['id'])[0]
         toEdit.rxuid = int(request.POST['rxuid'])
         toEdit.medName = RxNorm.getName(request.POST['rxuid'])
         toEdit.lot = int(request.POST['lot'])
         toEdit.expiration = request.POST['expiration']
         toEdit.save()
         # TODO: implement lastupdatetime
      if request.POST['requestType'] == 'deleteCompartment':
      # TODO: Implement this?
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

def updatecompartment(request):
   if request.method == 'POST':
      compID = request.POST['compID']
      ndc = request.POST['ndc']
      # need to convert to rxuid
      lot = request.POST['lot']
      expiration = request.POST['expiration']
      
      if request.POST['requestType'] == "compID":
         nextType = 'ndc'
         message = "Scan NDC"
      elif request.POST['requestType'] == 'ndc':
         message = "Scan Lot #"
         nextType = 'lot'
      elif request.POST['requestType'] == 'lot':
         message = "Scan expiration"
         nextType = 'expiration'
      elif request.POST['requestType'] == 'expiration':
         message = "Confirm info?"
         nextType = 'save'
      elif request.POST['requestType'] == 'save':
         if(compartment.objects(id=compID)[0]):
            toEdit = compartment.objects(id=compID)[0]
            toEdit.rxuid = int(RxNorm.getRXUID(ndc))
            toEdit.lot = int(lot)
            toEdit.expiration = expiration
            toEdit.save()
            message = "Save successful!"
            # TODO: implement lastupdatetime
         else:
            message = "Compartment not found"
         return render_to_response('updatecompartment.html', {'message': message}, context_instance=RequestContext(request))
      
      return render_to_response('updatecompartment.html', {'compID': compID, 'ndc': ndc, 'lot': lot, 'expiration': expiration, 'nextType': nextType, 'message': message}, context_instance=RequestContext(request))      
      
   return render_to_response('updatecompartment.html', {}, context_instance=RequestContext(request))