import urllib2
import json

def getJSON(url):
   req = urllib2.Request(url, None, {'Accept': 'application/json'})
   response = urllib2.urlopen(req)
   ret = json.loads(response.read(), 'utf-8')
   response.close()
   return ret
   
def getRXUID(ndc):
   json = getJSON(''.join(['http://rxnav.nlm.nih.gov/REST/rxcui?idtype=ndc&id=', str(ndc)]))
   if(json['idGroup']['rxnormId']):
      return json['idGroup']['rxnormId'][0]
   return 0
   
def getName(rxuid):
   names = getJSON(''.join(['http://rxnav.nlm.nih.gov/REST/rxcui/', str(rxuid), '/allProperties?prop=names']))
   if names['propConceptGroup']:
      name = names['propConceptGroup']['propConcept'][0]['propValue']
      return name
   else:
      return None
 
def getStrength(rxuid):
   names = getJSON(''.join(['http://rxnav.nlm.nih.gov/REST/rxcui/', str(rxuid), '/strength']))
   #if names['propConceptGroup']:
   strength = names['strengthGroup']['strength']
   
   if strength == '':
      return 20
   # return correct value for tylenol
   return strength.split()[0]