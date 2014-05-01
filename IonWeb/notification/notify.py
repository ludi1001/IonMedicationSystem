from django.core.management.base import BaseCommand, CommandError
from notification.models import medNotification, MedExpiration
from account.models import IonUser
from helper import helper
from dispenser.models import compartment
from datetime import datetime, timedelta, date

def runNotify():
   missed = datetime.now()-timedelta(hours=2)
   minusone = datetime.now()-timedelta(hours=1)
   now = datetime.now()
   plusone = datetime.now()+timedelta(hours=1)
   
   # set the flag for the newly active
   timeset = [plusone.strftime("%I:00%p").lower()]
   SetFlagPatients = helper.active_medications(timeset, 0)
   for Patient in SetFlagPatients:
      for medication in Patient.medications:
         if medication['active'] == True:           
            if any(True for x in medication['times'] if x in timeset):
               if medication['rxuid'] not in Patient.activeMeds:
                  Patient.activeMeds.append(medication['rxuid'])
                  Patient.save()
                  print "set flag for " + medication['rxuid']

   # notify the now and 1 hour ago people
   timeset = [now.strftime("%I:00%p").lower(), minusone.strftime("%I:00%p").lower()]
   NotificationPatients = helper.active_medications(timeset, 1);
   for Patient in NotificationPatients:
      for rxuid in Patient.activeMeds:
        # if any(True for x in medication['times'] if x in timeset):
            if Patient.user:
               newNotification = medNotification(target=Patient.user, type="reminder", generator = "CRON", rxuid = rxuid, patientName = Patient.firstName + Patient.lastName, time = now.strftime("%I:00%p"))
               newNotification.save()
            else:
               print Patient.firstName + " " + Patient.lastName + " doesn't have an Ion Account"
               
            print "notify " + rxuid

   timeset = [missed.strftime("%I:00%p").lower()]
   MissedPatients = helper.active_medications(timeset, 1) 
   
   # remove from activeMeds and mark them as medication missed
   # doesn't work if patient is returned anyways and has taken one of their medications
   for Patient in MissedPatients:
      for medication in Patient.medications:
         if any(True for x in medication['times'] if x in timeset) and medication['rxuid'] in Patient.activeMeds and medication['active'] == True:
            missedEntry = {}
            missedEntry['rxuid'] = medication['rxuid']
            missedEntry['quantity'] = medication['quantity']
            missedEntry['time'] = missed.strftime("%I:00%p").lower()
            missedEntry['timestamp'] = now
            
            Patient.medHistory.append({ 'MedicationMissed' : missedEntry })
            Patient.save()
            if medication['rxuid'] in Patient.activeMeds:
               Patient.activeMeds.remove(medication['rxuid'])
            # notify caretaker
            if Patient.caretaker:
               newNotification = medMissedNotification(target=Patient.caretaker, type="missed", generator = "CRON", rxuid = medication['rxuid'], patientName = Patient.firstName + Patient.lastName, time = missed.strftime("%I:00%p"))
             
               newNotification.save()
            print "patient missed  " + medication['rxuid']
   
   # daily checks for expiration
   if now.strftime("%I:00%p").lower() == '01:00am':
      for Compartment in compartment.objects():
         # will expire soon or has already expired
         if Compartment.expiration:
            if Compartment.expiration < datetime.now()+timedelta(days=2):
               CompartmentInfo = helper.findCompartment(Compartment.id)
               Dispenser = CompartmentInfo[0]
               SlotNum = CompartmentInfo[1] + 1
               caretakers = helper.getCaretakers()
               for caretaker in caretakers:
                  newNotification = MedExpiration(target=caretaker, type="expiration", generator = "CRON", rxuid = Compartment.rxuid, dispenser=Dispenser.user, slotNum = SlotNum, expirationDate = Compartment.expiration)
          
                  newNotification.save()
               print "notified caretakers about expired medication in " + str(Dispenser.location) + " dispenser, compartment " + str(SlotNum)