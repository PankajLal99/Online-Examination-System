from django.urls import path
from . import views

urlpatterns=[
    path('login/',views.loginPage,name='login'),
    path('logout/',views.LogoutPage,name='logout'),
    path('signup/',views.SignupPage,name='signup'),
    path('signupteacher/',views.SignupPageTeacher,name='signupteacher'),
    path('sent/', views.activation_sent_view, name="activation_sent"),
    path('invalid/', views.activation_invalid, name="activation_invalid"),
    path('details/student/',views.complete_info_stud,name='details_stud'),
    path('details/teacher/',views.complete_info_teach,name='details_teach'),
    path('activate/<slug:uidb64>/<slug:token>/', views.Activate, name='activate'),
]