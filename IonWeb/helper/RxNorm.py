import urllib2
import json

def getJSON(url):
   req = urllib2.Request(url, None, {'Accept': 'application/json'})
   response = urllib2.urlopen(req)
   ret = json.loads(response.read(), 'utf-8')
   response.close()
   return ret
   
def getName(rxuid):
   #url = ''.join(['http://rxnav.nlm.nih.gov/REST/rxcui/', rxuid])
   
   #attributes = RxNorm.getJSON(''.join([url, '/allProperties?prop=attributes']))
   #ndcs = RxNorm.getJSON(''.join([url, '/ndcs']))
   #ndc = ndcs['ndcGroup']['ndcList']['ndc'][0]
   names = getJSON(''.join(['http://rxnav.nlm.nih.gov/REST/rxcui/', rxuid, '/allProperties?prop=names']))
   name = names[propConceptGroup][propConcept][0][propValue]
   return name