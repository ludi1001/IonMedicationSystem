from models import IonUser

def IonAccessControl(request):
  group = {'user_group':None}
  if request.user.is_authenticated():
    user = IonUser.objects(user=request.user)[0]
    group['user_group'] = user.group
  return group