from django.shortcuts import render
from django.http import HttpResponse

from mongoengine import django
import mongoengine.django.mongo_auth.models
from mongoengine.django.auth import User

from django.contrib.auth import authenticate
import django.contrib.auth as auth
from django.contrib.auth.decorators import login_required

import hashlib
"""
def login(request):
    user = User(username==request.POST['username'])
    if user.password == hashlib.sha256(request.POST['password']).hexdigest():
        request.session['user_id'] = user._id
        request.session['user_type'] = user.user_type
        return HttpResponse("Login successful")
    else:
        return HttpResponse("Login failed")
"""

def create(request):
    user = User.create_user('john', 'password', 'lennon@thebeatles.com')
    user.save()
    return HttpResponse("Account create successful")
    
def login(request):
    user = authenticate(username='john', password='password')
    auth.login(request, user)
    if user is None:
        return HttpResponse("Login failed")
    else:
        return HttpResponse("Login successful")
        
@login_required
def restricted(request):
    return HttpResponse("Hai")

@login_required
def test(request):
    return HttpResponse("Bai")

def logout(request):
    """
    try:
        del request.session['user_id']
        del request.session['user_type']
    except:
        pass
    """
    auth.logout(request)
    return HttpResponse("Logout")
    return HttpResponse("Logged out")
