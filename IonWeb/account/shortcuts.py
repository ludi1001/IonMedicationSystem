from models import IonUser

def get_ion_user(request):
  return IonUser.objects(user=request.user)[0]
