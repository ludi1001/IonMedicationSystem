from django.core.management.base import BaseCommand, CommandError
from DataEntry.models import patient
from notification.models import notification
#from notification.views import active_medications
from datetime import datetime, timedelta, date

class Command(BaseCommand):
   # args = '<poll_id poll_id ...>'
   help = 'Generates notifications'

   def handle(self, *args, **options):
      missed = datetime.now()-timedelta(hours=2)
      minusone = datetime.now()-timedelta(hours=1)
      now = datetime.now()
      plusone = datetime.now()+timedelta(hours=1)
      
      
   
      # set the flag for the newly active
      timeset = [plusone.strftime("%I:00%p").lower()]
      SetFlagPatients = active_medications(timeset, 0)
      for Patient in SetFlagPatients:
         for medication in Patient.medications:
            for time in medication['times']:
               if time in timeset:
                  if medication['rxuid'] not in Patient.activeMeds:
                     Patient.activeMeds.append(medication['rxuid'])
                     Patient.save()
                     print "set flag for " + medication['rxuid']
      
      # notify the now and 1 hour ago people
      timeset = [now.strftime("%I:00%p").lower(), minusone.strftime("%I:00%p").lower()]
      NotificationPatients = active_medications(timeset, 1);
      for Patient in NotificationPatients:
         for medication in Patient.medications:
            for time in medication['times']:
               if time in timeset:
                  # newNotification = notification(target=Patient, type="medReminder", generator = "CRON")
                  # newNotification.save()
                  print "notify " + medication['rxuid']
   
      timeset = [missed.strftime("%I:00%p").lower()]
      MissedPatients = active_medications(timeset, 1)
      
      # remove from activeMeds and mark them as medication missed
      for Patient in NotificationPatients:
         for medication in Patient.medications:
            for time in medication['times']:
               if time in timeset:
                  missedEntry = {}
                  missedEntry['rxuid'] = medication['rxuid']
                  missedEntry['quantity'] = medication['quantity']
                  missedEntry['time'] = now.strftime("%I:00%p").lower()
                  Patient.medHistory.append({ 'MedicationMissed' : missedEntry })
                  Patient.save()
                  print "patient missed  " + medication['rxuid']
   
      timeset = [missed.strftime("%I:00%p").lower()]
      MissedPatients = active_medications(timeset, 1)
      
# LOGAN: This also caused the same/similar error when I tried to use this function by importing from notification.views
def active_medications(timeset, mode): 
   # elemMatch ensures the matched elements occur in the same medication instance  
   if mode == 1:
      ActivePatients = patient.objects(__raw__={ 'medications' : { '$elemMatch' : { 'times' : {'$in': timeset }, 'startDate' : { "$lte" : datetime.now().strftime("%Y-%m-%d") } } }, 'activeMeds' : { '$not': {'$size': 0}}})
   elif mode == 0:
      ActivePatients = patient.objects(__raw__={ 'medications' : { '$elemMatch' : { 'times' : {'$in': timeset }, 'startDate' : { "$lte" : datetime.now().strftime("%Y-%m-%d") } } } })
   
   return ActivePatients
   
   # medDict = {};
   
   # # TODO: check medication taken history?
   # for active_patient in ActivePatients:
      # medications = [];
      # for medication in active_patient.medications:
         # for time in medication['times']:
            # if time in timeset:
               # print "search for " + medication['rxuid']
               # medications.append(medication);
         
      # medDict[active_patient] = medications;

   # return medDict
      