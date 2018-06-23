import requests
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, UserRegistrationForm
from py2neo import Graph

graph = Graph(host='neo4j_db', password='_genius01_', scheme='bolt')

# Create your views here.
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                                username=cd['username'],
                                password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
            else:
                return HttpResponse('Disabled account')
        else:
            return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})


@login_required
def dashboard(request):
    social_user = request.user.social_auth.filter(
        provider='facebook',
    ).first()
    if social_user: # try facebook login
        url = 'https://graph.facebook.com/{0}/'.format(social_user.uid)
        res = requests.get(url, {'fields':'email,picture,name,id,location', 'access_token':social_user.extra_data['access_token']}).json()
        query = 'match (p:Person)-[:STUDIED]-(info:StudyInfo) where p.firstname_en="%s" and p.lastname_en="%s" return info'
        query = query % (request.user.first_name.lower(), request.user.last_name.lower())
        studyinfo = list(graph.run(query))[0].get('info')
        country = studyinfo.get('country','')
        specialty = studyinfo.get('specialty','')
        fos = studyinfo.get('field_of_study','')
        degree = studyinfo.get('degree_title', '')
        return render(request,
                  'account/dashboard.html',
                  {'section': 'dashboard',
                   'picture_url': res['picture']['data']['url'],
                   'name': res['name'],
                   'email': res.get('email', None),
                   'country': country,
                   'specialty': specialty,
                   'fos': fos,
                   'degree': degree,
                   })
    else: # try google login
        social_user = request.user.social_auth.filter(
            provider='google-oauth2',
        ).first()
        if social_user:
            google_token = social_user.extra_data['access_token']
            url = 'https://www.googleapis.com/oauth2/v1/userinfo'.format(social_user.uid)
            res = requests.get(url, {'access_token': google_token, 'alt': 'json'}).json()
            return render(request,
                    'account/dashboard.html',
                    {'section': 'dashboard',
                    'picture_url': res.get('picture'),
                    'name': res.get('name'),
                    'email': res.get('email', None),
                    })
        else:
            is_scholar_student = False
            return render(request,
                    'account/dashboard.html',
                    {'section': 'dashboard',
                    'name': u'{} {}'.format(request.user.first_name, request.user.last_name),
                    'email': request.user.email,
                    'is_scholar_student': False
                    })
    return render(request,
                'account/dashboard.html',
                {'section': 'dashboard'})


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(
                user_form.cleaned_data['password']
            )
            new_user.save()
            return render(request,
                          'account/register_done.html',
                          {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request,
                  'account/register.html',
                  {'user_form': user_form})
