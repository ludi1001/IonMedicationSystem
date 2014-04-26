import datetime
from helper import RxNorm, helper
from models import dispenser
from models import compartment
from DataEntry.models import patient
from django.template import RequestContext
from django.shortcuts import render_to_response

def management(request):
   if request.method == 'POST':
      
      if request.POST['requestType'] == 'removeCompartment':
         compID = request.POST['compID']
         dispID = request.POST['dispID']
         Dispenser = dispenser.objects(id=dispID)[0]
         
         for index, Compartment in enumerate(Dispenser.slots):
            if Compartment:
               if str(Compartment.id) == compID:
                  Dispenser.slots[index] = None
                  Dispenser.save()
                  Compartment.loaded = False
                  Compartment.save()
            
   return render_to_response('dispenser.html', {'dispensers': dispenser.objects, 'compartments': compartment.objects}, context_instance=RequestContext(request))

def compartments(request):
   if request.method == 'POST':      
    #  if request.POST['requestType'] == 'expiration'
      if request.POST['requestType'] == 'updateCompartment':
         toEdit = compartment.objects(id=request.POST['id'])[0]
         toEdit.rxuid = int(request.POST['rxuid'])
         toEdit.medName = RxNorm.getName(request.POST['rxuid'])
         toEdit.lot = int(request.POST['lot'])
         toEdit.expiration = request.POST['expiration']
         toEdit.save()
         # TODO: implement lastupdatetime
   return render_to_response('compartment.html', {'compartments': compartment.objects()}, context_instance=RequestContext(request))

def loadcompartment(request):
   message = ''
   if request.method == 'POST':
      dispID = request.POST['dispID']
      compID = request.POST['compID']
      Compartment = compartment.objects(id=compID)[0]
      slotNum = int(request.POST['slotNum'])
      disp = dispenser.objects(id=dispID)[0]
         
      if not Compartment.loaded and disp.slots[slotNum] == None:
         Compartment.loaded = True
         Compartment.save()
         disp.slots[slotNum] = Compartment
         disp.save()    
         message = "Loaded compartment into slot number " + str(slotNum)
         
      else:
         message = "Invalid operation (compartment loaded in another slot or slot is filled already)"

   return render_to_response('loadcompartment.html', {'message' : message, 'compartments' : compartment.objects(loaded=False), 'dispensers' : dispenser.objects()}, context_instance=RequestContext(request))

def updatecompartment(request):
   if request.method == 'POST':
      compID = request.POST['compID']
      ndc = request.POST['ndc']
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
   
def updateRFID(request):
   compData = ""
   
   if request.method == 'POST':
      RFID = request.POST['rfid']
      compData = compartment.objects(rfid = RFID)[0]

   return render_to_response('scanrfid.html', {'compData': compData}, context_instance=RequestContext(request))

def dispenser_view(request):
   params = {}
   if 'dispenserID' in request.GET:
      dispID = request.GET['dispenserID']
      Dispenser = dispenser.objects(id=dispID)[0]
      params['dispenser'] = Dispenser
      
      if request.method == 'POST':
         patientID = request.POST['patientID']
         Patient = patient.objects(id=patientID)[0]
         
         if request.POST['requestType'] == 'takeMed':
            rxuid = request.POST['rxuid']
                        
            for medication in Patient.medications:
               if medication['rxuid'] == rxuid:
                  toTake = medication
            
            helper.take_medication(Patient, toTake['rxuid'], toTake['quantity'], dispID)

            compNum = request.POST['compartment']
            
            print "Arduino needs to dispense" + toTake['quantity'] + " pills from compartment " + compNum
            # compartment, index, pills, weight
         if request.POST['requestType'] == 'scannedID' or request.POST['requestType'] == 'takeMed':   
            validMedications = {}
            for rxuid in Patient.activeMeds:
               for index, Compartment in enumerate(Dispenser.slots):
                  if Compartment:
                     if int(rxuid) == Compartment.rxuid:
                        validMedications['index'] = rxuid
                        
         if len(validMedications) == 0:
            params['message'] = "No valid medications at this time"
         params['validMedications'] = validMedications
         params['patientID'] = patientID
      
   else:
      params = {'message' : "No dispenser specified"}
      
   return render_to_response('dispenser_view.html', params, context_instance=RequestContext(request))

def dispenser_admin(request):
   newID = ""
   if request.method == 'POST':
      if request.POST['requestType'] == 'newDispenser':
         location = request.POST['location']
         newDispenser = dispenser(location=location)
         newDispenser.creationTime = datetime.datetime.now()
         newDispenser.slots = [ None for i in range(6)];
         newDispenser.save()
      if request.POST['requestType'] == 'deleteDispenser':
         id = request.POST['id']
         Dispenser = dispenser.objects(id=id)[0]
         
         for Compartment in Dispenser.slots:
            if Compartment:
               Compartment.loaded = False
               Compartment.save()
               
         Dispenser.delete()
      if request.POST['requestType'] == 'newCompartment':
         newCompartment = compartment(loaded = False)
         newCompartment.save()
         newID = newCompartment.id
      if request.POST['requestType'] == 'deleteCompartment':
      # TODO: Implement this? Need to remove from dispenser
         id = request.POST['id']
         compartment.objects(id=id)[0].delete()

   return render_to_response('dispenser_admin.html', {'compartments' : compartment.objects(), 'dispensers' : dispenser.objects(), 'newID' : newID}, context_instance=RequestContext(request))
