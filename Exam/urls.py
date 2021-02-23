from django.urls import path
from . import views

urlpatterns=[
    path('',views.HomePage,name='home'),
    path('addquiz/',views.AddQuiz,name='addquiz'),
    path('profile/',views.profile,name='profile'),
    path('submitaddquiz/',views.submitquizquestion,name='qsubmit'),
    path('deletequiz/<int:pk>/',views.deletequiz,name='deletequiz'),
    path('publish/<int:pk>/',views.publish,name='publish'),
    path('unpublish/',views.unpublish,name='unpublish'),
    path('addqna/<slug:slug>',views.AddQnA,name='addqna'),
    path('attemptquiz/<slug:slug>/',views.AttemptQuiz,name='attemptquiz'),
    path('submitquiz/',views.SubmitQuiz,name='submitquiz'),
    path('viewresponse/<int:pk>/',views.ViewResponse,name='viewresponse'),
    path('report/<int:pk>',views.Report,name='report'),
    path('send/<int:pk>',views.sendreport,name='send'),
    path('video/',views.video,name='video'),
]