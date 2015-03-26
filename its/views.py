from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.contrib import messages
from .users.forms import UserForm
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    """
    Default home view
    """

    return render(request, 'home.html')
