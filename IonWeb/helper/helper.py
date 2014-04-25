from DataEntry.models import patient
from datetime import datetime, timedelta, date

# can't import from notifications.views...
def active_medications(timeset, mode): 
   # elemMatch ensures the matched elements occur in the same medication instance  
   if mode == 1:
      ActivePatients = patient.objects(__raw__={ 'medications' : { '$elemMatch' : { 'times' : {'$in': timeset }, 'startDate' : { "$lte" : datetime.now().strftime("%Y-%m-%d") } } }, 'activeMeds' : { '$not': {'$size': 0}}})
   elif mode == 0:
      ActivePatients = patient.objects(__raw__={ 'medications' : { '$elemMatch' : { 'times' : {'$in': timeset }, 'startDate' : { "$lte" : datetime.now().strftime("%Y-%m-%d") } } } })
      # TODO: if last medication taken time was # days ago
      # TODO: if dispensable = true
      # TODO: if medication.active = true
   return ActivePatients
   
def take_medication(Patient, rxuid, quantity, dispenserID):
   medEntry = {}
   medEntry['rxuid'] = rxuid
   medEntry['quantity'] = quantity
   medEntry['timestamp'] = datetime.now()
   medEntry['dispenserID'] = dispenserID;
   
   Patient.medHistory.append({ 'MedicationTaken' : medEntry })
   Patient.activeMeds.remove( rxuid )
   Patient.save()
   
   return Patient.firstName + " " + Patient.lastName + " took medication " + rxuid 
   