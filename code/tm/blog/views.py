from django.shortcuts import render
from django.http import HttpResponseRedirect

# Create your views here.

def switch_lang(request):
    if request.session.get('language', None) is None:
        request.session['language'] = 'th'
    elif request.session.get('language') == 'en':
        request.session['language'] = 'th'
    elif request.session.get('language') == 'th':
        request.session['language'] = 'en'
    print(request.session.get('language'))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
