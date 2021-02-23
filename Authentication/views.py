from django.shortcuts import render,redirect, get_object_or_404, HttpResponseRedirect
from .models import *
#login
# from django.contrib.auth.forms import UserCreationForm
from . import forms
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login,logout,authenticate

# activations
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_text
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from .tokens import account_activation_token
from django.template.loader import render_to_string

#sending email
from django.core.mail import send_mail,BadHeaderError
from django.conf import settings 

#custom decorator
from .decorators import *
#group management
from django.contrib.auth.models import Group

@unauthenticated_user
def loginPage(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        user= authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.info(request,'Userrname or Password is Incorrect')
            return redirect('login')
    context={}
    return render(request,'Authentication/login.html')

def LogoutPage(request):
    logout(request)
    messages.info(request,'Logged Out Successfully!')
    return redirect('login')

def activation_sent_view(request):
    return render(request, 'Authentication/activation_sent.html')

def activation_invalid(request):
    return render(request, 'Authentication/activation_invalid.html')


def Activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    # checking if the user exists, if the token is valid.
    if user is not None and account_activation_token.check_token(user, token):
        # if valid set active true 
        user.is_active = True
        # set signup_confirmation true
        user.student.signup_confirmation = True
        user.save()
        login(request, user)
        messages.info(request,'Profile Activated Successfully !!')
        return redirect('home')
    else:
        return render(request, 'Authentication/activation_invalid.html')

@unauthenticated_user
def SignupPage(request):
    if request.method=='POST':
        form = forms.SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            '''Add group while register below two lines'''
            group= Group.objects.get(name='student')
            user.groups.add(group)
            '''Till here'''
            user.refresh_from_db()
            user.student.first_name = form.cleaned_data.get('first_name')
            user.student.last_name = form.cleaned_data.get('last_name')
            user.student.email = form.cleaned_data.get('email')
            # user can't login until link confirmed
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            # messages.success(request,"User Created Successfully for "+username)
            subject = 'Please Activate Your Account'
            # load a template like get_template() 
            # and calls its render() method immediately.
            message = render_to_string('Authentication/activation_request.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                # method will generate a hash value with user related data
                'token': account_activation_token.make_token(user),
            })
            try:
                email_from = settings.EMAIL_HOST_USER 
                send_mail(subject,
                message,email_from,
                [user.student.email,]
                ,fail_silently=False,)
                messages.info(request,'Activation Link Sent Successfully !!')
                return redirect('login')
            except BadHeaderError:
                return HttpResponse('Invalid header found.')  
    else:
        form = forms.SignUpForm()
    return render(request,'Authentication/signup.html',{'form': form})

@unauthenticated_user
def SignupPageTeacher(request):
    if request.method=='POST':
        form = forms.SignUpFormTeacher(request.POST)
        if form.is_valid():
            user = form.save()
            '''Add group while register below two lines'''
            group= Group.objects.get(name='teacher')
            user.groups.add(group)
            '''Till here'''
            
            user.refresh_from_db()
            user.teacher.first_name = form.cleaned_data.get('first_name')
            user.teacher.last_name = form.cleaned_data.get('last_name')
            user.teacher.email = form.cleaned_data.get('email')
            # user can't login until link confirmed
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            # messages.success(request,"User Created Successfully for "+username)
            subject = 'Please Activate Your Account'
            # load a template like get_template() 
            # and calls its render() method immediately.
            message = render_to_string('Authentication/activation_request.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                # method will generate a hash value with user related data
                'token': account_activation_token.make_token(user),
            })
            try:
                email_from = settings.EMAIL_HOST_USER 
                send_mail(subject,
                message,email_from,
                [user.teacher.email,]
                ,fail_silently=False,)
                messages.info(request,'Activation Link Sent Successfully !!')
                return redirect('login')
            except BadHeaderError:
                return HttpResponse('Invalid header found.')  
    else:
        form = forms.SignUpFormTeacher()
    return render(request,'Authentication/signup.html',{'form': form})

def complete_info_teach(request):
    teach=Teacher.objects.get(user=request.user)
    form=forms.TeacherForm(instance=teach)
    if request.method=="POST":
        form=forms.TeacherForm(request.POST,instance=teach)
        if form.is_valid():
            form.save()
        return redirect('home')
    return render(request,'Authentication/complete_info.html',{'form': form,'details':"Complete Teacher Details"})

def complete_info_stud(request):
    stud=Student.objects.get(user=request.user)
    form=forms.StudentForm(instance=stud)
    if request.method=="POST":
        form=forms.StudentForm(request.POST,instance=stud)
        if form.is_valid():
            form.save()
        return redirect('home')
    return render(request,'Authentication/complete_info.html',{'form': form , 'details':"Complete Student Details"})