# -*- coding: utf-8 -*-
import requests
from collections import defaultdict
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from sqlalchemy import create_engine
from py2neo import Graph
from .models import Profile
from social_django.utils import psa
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .token import account_activation_token
from django.core.mail import EmailMessage



# graph = Graph(host='neo4j_db', password='_genius01_', scheme='bolt')
engine = create_engine('postgresql+psycopg2://postgres:_genius01_@postgres_db/keywordsdw')
conn = engine.connect()

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
        print(picture_url)
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

    name_th = u'{} {}'.format(user.profile.first_name_th, user.profile.last_name_th)
    name_en = u'{} {}'.format(user.first_name, user.last_name)

    profile_photo = picture_url if social_user else user.profile.photo
    scopus_id = user.profile.scopus_id
    abstracts = []
    keywords = []
    fields = defaultdict(int)
    if scopus_id:
        author = conn.execute("select * from authors where scopus_id='%s'" % scopus_id).fetchone()
        if author:
            query = ("select word_en from keywords where author_scopus_id='%s'" % scopus_id)
            results = conn.execute(query).fetchall()
            for rec in results:
                keywords.append(rec[0])

            query = ("select abstracts.id,abstracts.title_en from abstracts inner join abstract_has_author "
                     "on abstract_has_author.abstract_id=abstracts.id inner join "
                     "authors on abstract_has_author.author_id=authors.id "
                     "where authors.id=%s" % author.id)
            abstracts = conn.execute(query).fetchall()
            for abstract in abstracts:
                query = ("select name from research_fields inner join field_has_abstract on "
                         "field_has_abstract.field_id=research_fields.id inner join "
                         "abstracts on field_has_abstract.abstract_id=abstracts.id "
                         "where abstracts.id=%d" % int(abstract[0]))
                results =  conn.execute(query).fetchall()
                for f in results:
                    fields[f[0]] += 1
    fields.default_factory = None
    sqlquery = "select * from tm_researcher_profile where lower(first_name_en)='{}' and lower(last_name_en)='{}'".format(user.first_name.lower(),user.last_name.lower())
    results = conn.execute(sqlquery)
    return render(request,
            'account/dashboard.html',
            {'section': 'dashboard',
            'name_th': name_th,
            'name_en': name_en,
            'picture_url': profile_photo,
            'profile': user.profile,
            'degree': degrees.get(user.profile.degree, ''),
            'user': user,
             'abstracts': abstracts,
             'keywords': keywords,
             'fields': fields,
             'matches': results,
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
            return redirect('tm_account', new_user_id=new_user.id)
    else:
        user_form = UserRegistrationForm()
    return render(request,
                  'account/register.html',
                  {'user_form': user_form})


def link_tm_account(request, new_user_id):
    user = User.objects.get(pk=new_user_id)
    sqlquery = "select * from tm_researcher_profile where lower(first_name_en)='{}' and lower(last_name_en)='{}'".format(user.first_name.lower(),user.last_name.lower())
    results = conn.execute(sqlquery)
    return render(request,
                  'account/register_done.html',
                  {'new_user': user, 'matches': results})


def verify_email(request, user_id, profile_id):
    user = User.objects.get(pk=user_id)
    sqlquery = "select * from tm_researcher_profile where id={}".format(profile_id)
    tm = conn.execute(sqlquery).first()
    email = tm['email']
    current_site = get_current_site(request)
    mail_subject = 'Confirm your email to link account.'
    message = render_to_string('account/acc_active_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
        'pid': urlsafe_base64_encode(force_bytes(profile_id)).decode(),
        'token': account_activation_token.make_token(user),
    })
    email = EmailMessage(
        mail_subject, message, to=[email]
    )
    email.send()
    return render(request, 'account/verify_mail.html', {'status': 'pending'})


def activate_link(request, uidb64, pidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        pid = force_text(urlsafe_base64_decode(pidb64))
        sqlquery = 'select * from tm_researcher_profile where id={}'.format(pid)
        profile = conn.execute(sqlquery).first()
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.profile.tm_profile_id = int(profile['id'])
        user.profile.save()
        login(request, user,backend='django.contrib.auth.backends.ModelBackend')
        # return redirect('home')
        return render(request, 'account/verify_mail.html', {'status': 'succeeded', 'user': user, 'profile': profile})
    else:
        return HttpResponse('Activation link is invalid!')


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

from rest_framework_jwt.settings import api_settings


@psa('social:complete')
def register_by_access_token(request, backend):
    # This view expects an access_token GET parameter, if it's needed,
    # request.backend and request.strategy will be loaded with the current
    # backend and strategy.
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

    token = request.GET.get('access_token')
    user = request.backend.do_auth(token)
    if user:
        login(request, user)
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        return JsonResponse({'token': token, 'user_id': user.id})
    else:
        return JsonResponse({'token': None, 'user_id': None})
