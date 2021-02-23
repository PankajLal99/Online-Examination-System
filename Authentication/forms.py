from django import forms
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class StudentForm(forms.ModelForm):
    class Meta:
        model=Student
        fields = '__all__'
        exclude=['user','signup_confirmation']

class TeacherForm(forms.ModelForm):
    class Meta:
        model=Teacher
        fields = '__all__'
        exclude=['user','signup_confirmation']

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, help_text='First Name')
    last_name = forms.CharField(max_length=100, help_text='Last Name')
    email = forms.EmailField(max_length=200,help_text='Email Address')
    
    class Meta:
        model = User
        fields = ('username','first_name', 'last_name','email','password1','password2')

class SignUpFormTeacher(UserCreationForm):
    first_name = forms.CharField(max_length=100, help_text='First Name')
    last_name = forms.CharField(max_length=100, help_text='Last Name')
    email = forms.EmailField(max_length=200,help_text='Email Address')
    
    class Meta:
        model = User
        fields = ('username','first_name', 'last_name','email','password1','password2')