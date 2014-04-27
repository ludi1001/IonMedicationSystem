from django.shortcuts import redirect
from models import IonUser

def get_ion_user(request):
  return IonUser.objects(user=request.user)[0]

def choose_group_dependent_page(request, **kwargs):
  user = get_ion_user(request)
  if user.group in kwargs:
    return kwargs[user.group](request, user)
  return redirect('/account/login')