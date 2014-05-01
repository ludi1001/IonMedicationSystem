import datetime
from mongoengine.django.auth import User
from helper import RxNorm, helper
from models import dispenser
from models import compartment
from DataEntry.models import patient
from account.models import IonUser
from account.privilege_tests import is_in_group, DISPENSER_GROUP
from django.shortcuts import render
import re

def management(request):
   params = {'dispensers': dispenser.objects.order_by('location'), 'compartments': compartment.objects}
   
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
      
      if request.POST['requestType'] == 'deleteDispenser':
         id = request.POST['id']
         if dispenser.objects(id=id):
            Dispenser = dispenser.objects(id=id)[0]
            for Compartment in Dispenser.slots:
               if Compartment:
                  Compartment.loaded = False
                  Compartment.save()

               Dispenser.user.user.delete()
               Dispenser.delete()            
         else:
            params['message'] = "Page refresh - not a valid dispenser to delete"

      if request.POST['requestType'] == 'loadCompartment':
         dispID = request.POST['dispID']
         
   return render(request, 'dispenser.html', params)

def compartments(request):
   params = {}
   params['compartments'] = compartment.objects()
   if request.method == 'POST':
      # TODO: add quantity
      if request.POST['requestType'] == 'updateCompartment':
         if not request.POST.get('id'):
            params['message'] = 'No valid compartments to update'
         elif request.POST['rxuid'] == "":
            params['message'] = "Please enter an rxuid"
         elif RxNorm.getName(request.POST['rxuid']) == None:
            params['message'] = "Invalid rxuid"
         elif request.POST['lot'] == "":
            params['message'] = "Please enter a lot number"
         elif not helper.validate(request.POST['expiration']): 
           params['message'] = 'Expiration date must be mm-dd-yyy'
         else:  
            toEdit = compartment.objects(id=request.POST['id'])[0]         
            toEdit.rxuid = int(request.POST['rxuid'])
            toEdit.lot = int(request.POST['lot'])
            toEdit.expiration = request.POST['expiration']
            toEdit.save()
            params['message'] = 'Commpartment successfully updated!'
            params['message_type'] = 'success'
            
      if request.POST['requestType'] == 'clearCompartment':
         if not request.POST.get('id'):
            params['message'] = 'No valid compartments to clear'
         else:
            toEdit = compartment.objects(id=request.POST['id'])        
            toEdit.update_one(unset__rxuid='')
            toEdit.update_one(unset__lot='')
            toEdit.update_one(unset__expiration='')
            toEdit.update_one(unset__quantity='')
            toEdit[0].save()
            
   return render(request, 'compartment.html', params)

def loadcompartment(request):
   message = ''
   message_type = 'error'
   if request.method == 'POST':
      if not request.POST.get('dispID'):
         message = "No valid dispensers"
      elif not request.POST.get('compID'):
         message = "No valid compartments to load"
      else:
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
            message = "Loaded compartment into slot number " + str(slotNum + 1)
            message_type = "success"

         else:
            message = "Invalid operation (compartment loaded in another slot or slot is filled already)"

   return render(request, 'loadcompartment.html', {'message' : message, 'message_type': message_type, 'compartments' : compartment.objects(loaded=False), 'dispensers' :  dispenser.objects.order_by('location')})

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

   return render(request, 'updatecompartment.html', {})

def updateRFID(request):
   compData = ""

   if request.method == 'POST':
      RFID = request.POST['rfid']
      compData = compartment.objects(rfid = RFID)[0]

   return render(request, 'scanrfid.html', {'compData': compData})
   
def is_valid(str):
   return re.match("^[0-9a-fA-F]{24}$", str)

@is_in_group(DISPENSER_GROUP) 
def dispenser_view(request):
   params = {}
   #if 'dispenserID' in request.GET:
   dispID = dispenser.objects(user=request.user)[0].id #request.GET['dispenserID']
   if is_valid(dispID) and dispenser.objects(id=dispID):
      Dispenser = dispenser.objects(id=dispID)[0]
      params['dispenser'] = Dispenser
      if request.method == 'POST':
         userID = request.POST['userID']
         params['userID'] = userID
         
         if is_valid(userID) and IonUser.objects(id=userID):
            ionuser = IonUser.objects(id=userID)[0]
            if ionuser.group == "admin" or ionuser.group == "caretaker":
               # caretaker/admin stuff
               if request.POST['requestType'] == 'scannedID' or request.POST['requestType'] == 'takeMed':
                  validMedications = {}
                  myPatients = patient.objects(caretaker=ionuser.id)
                  for Patient in myPatients:
                     for rxuid in Patient.activeMeds:
                        for index, Compartment in enumerate(Dispenser.slots):
                           if Compartment:
                              if int(rxuid) == Compartment.rxuid:
                                 validMedications[rxuid] = index, Patient, True
                  params['validMedications'] = validMedications
                  params['caretaker'] = True
            elif ionuser.group == "patient":
               Patient = patient.objects(user=ionuser.id)[0]
      
               if request.POST['requestType'] == 'scannedID' or request.POST['requestType'] == 'takeMed':
                  validMedications = {}
                  for rxuid in Patient.activeMeds:
                     for index, Compartment in enumerate(Dispenser.slots):
                        if Compartment:
                           if int(rxuid) == Compartment.rxuid:
                              validMedications[rxuid] = index, Patient, False
                     
               if len(validMedications) == 0:
                  params['message'] = "No valid medications at this time"
               print validMedications
               params['validMedications'] = validMedications
               
            if request.POST['requestType'] == 'takeMed':
               rxuid = request.POST['rxuid']
               caretaker = request.POST['caretaker']
               
               Patient = patient.objects(id=request.POST['patientID'])[0]
   
               for medication in Patient.medications:
                  if medication['rxuid'] == rxuid and medication['active'] == True:
                     toTake = medication

               helper.take_medication(Patient, toTake['rxuid'], toTake['quantity'], dispID, caretaker)

               compNum = str(request.POST['compartment'])
               params['message'] = "Successfully took medication"
               
               del params['validMedications'][rxuid]
               
               print "Arduino needs to dispense " + toTake['quantity'] + " pills from compartment " + compNum + " of weight " + str(RxNorm.getStrength(rxuid))
               return render(request, 'dispense_medication.html', {"pills": toTake['quantity'], "compartment":compNum, "weight":RxNorm.getStrength(rxuid),
                  '_patient': Patient.id, '_rxuid': toTake['rxuid'], '_caretaker': caretaker})
         else:
            params['message'] = 'Invalid ID'

   else:
      params = {'message' : "Incorrect or no dispenser specified"}
   return render(request, 'dispenser_view.html', params)

def dispenser_admin(request):
   newID = ""
   if request.method == 'POST':
      if request.POST['requestType'] == 'newDispenser':
         location = request.POST['location'].strip()
         user = User.create_user(location, 'password')
         user.save()
         user = IonUser(user=user,group='dispenser',birthdate=datetime.datetime.now())
         user.save()
         newDispenser = dispenser(user=user,location=location)
         newDispenser.creationTime = datetime.datetime.now()
         newDispenser.slots = [ None for i in range(6)];
         newDispenser.save()
      if request.POST['requestType'] == 'newCompartment':
         newCompartment = compartment(loaded = False)
         newCompartment.save()
         newID = newCompartment.id
      if request.POST['requestType'] == 'deleteCompartment':
      # TODO: Implement this? Need to remove from dispenser
         id = request.POST['id']
         compartment.objects(id=id)[0].delete()

   return render(request, 'dispenser_admin.html', {'compartments' : compartment.objects(), 'dispensers' : dispenser.objects(), 'newID' : newID})

@is_in_group(DISPENSER_GROUP)   
def dispense_medication(request):
  return render(request, 'dispense_medication.html', {'compartment':0,'pills':2,'weight':100})
  
def load_compartment(request):
   params = {}
   # get dispenserID from user ID
   if 'dispenserID' in request.GET:
      dispID = request.GET['dispenserID']
      if is_valid(dispID) and dispenser.objects(id=dispID):
         Dispenser = dispenser.objects(id=dispID)[0]
         params['dispenser'] = Dispenser
      else:      
         params['message'] = 'Invalid dispenser ID'
         params['hide'] = True
      
      free = []
      for index, slot in enumerate(Dispenser.slots):
         if slot == None:
            free.append(index)
      params['free'] = free
      
      if len(free) == 0:
         params['message'] = "No free slots in this dispenser."
         params['hide'] = True
   else:
      params['message'] = "need dispenser ID"
      params['hide'] = True
      
   if request.method == 'POST':
      if request.POST['requestType'] == 'compID':
         Dispenser = dispenser.objects(id=request.POST.get('dispID'))[0]
         params['dispID'] = Dispenser.id
         compID = request.POST.get('compID')
         if is_valid(compID) and compartment.objects(id=compID):
            Compartment = compartment.objects(id=compID)[0]
            
            if not Compartment.rxuid:
               params['message'] = "Empty Compartment."
            
            elif Compartment.loaded == True:
               location = helper.findCompartment(compID)
               params['message'] = "Compartment already loaded in slot " + str((location[1] + 1)) + " in " + location[0].location + " dispenser."
            else:
               params['compID'] = compID
         else:
            params['message'] = "Not a valid compartment ID"
      
      # detect which slot?
      if request.POST['requestType'] == 'slotNum':
         Dispenser = dispenser.objects(id=request.POST.get('dispID'))[0]
         compID = request.POST.get('compID')
         Compartment = compartment.objects(id=compID)[0]
         slotNum = int(request.POST.get('slotNum'))   
            
         Compartment.loaded = True
         Compartment.save()
         Dispenser.slots[slotNum] = Compartment
         Dispenser.save()
         params['message'] = "Loaded compartment into slot number " + str(slotNum + 1)
         params['message_type'] = "success"

         if len(free) == 1:
            params['hide'] = True
   return render(request, 'updatecompartment.html', params)
