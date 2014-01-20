from django.shortcuts import render
from django.http import HttpResponse
from models import User

import hashlib

def login(request):
    user = User(username==request.POST['username'])
    if user.password == hashlib.sha256(request.POST['password']).hexdigest():
        request.session['user_id'] = user._id
        request.session['user_type'] = user.user_type
        return HttpResponse("Login successful")
    else:
        return HttpResponse("Login failed")
        

def logout(request):
    try:
        del request.session['user_id']
        del request.session['user_type']
    except:
        pass
    return HttpResponse("Logged out")
