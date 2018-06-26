# -*- coding: utf-8 -*-
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from py2neo import Graph
from .models import Profile

# graph = Graph(host='neo4j_db', password='_genius01_', scheme='bolt')

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


def social_login(request):
    return redirect(request.user.get_absolute_url())


def profile(request, username):
    user = get_object_or_404(User, username=username)
    degrees = {1: u"Bachelor", 2: "Master", 3: 'Doctorate'}
    social_user = user.social_auth.filter(
        provider='facebook',
    ).first()
    if social_user: # use facebook login
        url = 'https://graph.facebook.com/{0}/'.format(social_user.uid)
        res = requests.get(url, {'fields': 'picture.type(large)', 'access_token':social_user.extra_data['access_token']}).json()
        picture_url = res['picture']['data']['url']
    else: # use google login
        social_user = user.social_auth.filter(
            provider='google-oauth2',
        ).first()
        if social_user:
            google_token = social_user.extra_data['access_token']
            url = 'https://www.googleapis.com/oauth2/v1/userinfo'.format(social_user.uid)
            res = requests.get(url, {'access_token': google_token, 'alt': 'json'}).json()
            picture_url = res.get('picture')
        else:  # use username login
            picture_url = None

    if Profile.objects.filter(user=user).first() is None:
        messages.info(request, 'Please edit your profile by clicking at "edit profile" link.')
        Profile.objects.create(user=request.user)
    if social_user:
        if not user.profile.social_photo:
            user.profile.social_photo = picture_url
            user.profile.save()
            messages.info(request, 'You social profile photo has been added to your account.')

    name_th = u'{} {}'.format(user.profile.first_name_th, user.profile.last_name_th)
    name_en = u'{} {}'.format(user.first_name, user.last_name)

    profile_photo = user.profile.social_photo if social_user else user.profile.photo

    return render(request,
            'account/dashboard.html',
            {'section': 'dashboard',
            'name_th': name_th,
            'name_en': name_en,
            'picture_url': profile_photo,
            'profile': user.profile,
            'degree': degrees.get(user.profile.degree, ''),
            'user': user
            })


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(
                user_form.cleaned_data['password']
            )
            new_user.save()
            Profile.objects.create(user=new_user)
            return render(request,
                          'account/register_done.html',
                          {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request,
                  'account/register.html',
                  {'user_form': user_form})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile,
                            data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect(request.user.get_absolute_url())
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(request, 'account/edit_profile.html',
                    {'user_form': user_form, 'profile_form': profile_form})