from django.shortcuts import render,redirect
from django.views.decorators import gzip
from django.http import HttpResponse,StreamingHttpResponse,HttpResponseServerError
from .models import *
from .forms import *
from Authentication.forms import *
from django.core.paginator import Paginator
from django.contrib import messages
import json
#sending email
from django.core.mail import BadHeaderError
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import get_template
# import students from authentication
from Authentication import models as Authmodels
# camera and eye detection
import cv2
import dlib
import numpy as np
#login
from django.contrib.auth.decorators import login_required
#decorator
from .decorators import *
# Create your views here.

@login_required(login_url='login')
def HomePage(request):
    if request.user.groups.filter(name="student").exists():
        Quizes=Quiz.objects.filter(Branch=request.user.student.Branch,Sem=request.user.student.Sem,published=True)
        stud=Authmodels.Student.objects.get(user=request.user)
        if stud.RollNo is None:
            messages.success(request,"Successfully Filled Out the Known Information")
            return redirect("details_stud")
    elif request.user.groups.filter(name="teacher").exists():
        Quizes=Quiz.objects.filter(Branch=request.user.teacher.Branch,Sem=request.user.teacher.Sem,published=True)
        teach=Authmodels.Teacher.objects.get(user=request.user)
        if teach.UID is None:
            messages.success(request,"Successfully Filled Out the Known Information")
            return redirect("details_teach")
    else:
        Quizes=Quiz.objects.filter(published=True)
    context={'quizes':Quizes}
    return render(request,"Exam/Home.html",context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher'])
def AddQuiz(request):
    quizform=QuizForm(initial={'user':request.user})
    if request.method=='POST':
        quizform=QuizForm(request.POST,initial={'user':request.user})
        if quizform.is_valid():
            quiz=quizform.save(commit=False)
            quiz.user=request.user
            quiz.Branch=request.user.teacher.Branch
            quiz.Sem=request.user.teacher.Sem
            quiz.save()
            return redirect('/addqna/'+str(quiz.slug))
    else:
        quizform=QuizForm()
    context={'quizform':quizform}
    return render(request,"Exam/AddQuiz.html",context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher'])
def deletequiz(request,pk):
    Quiz.objects.get(id=pk).delete()
    messages.info(request," Deleted Successfully!!")
    return redirect('home')

@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher'])
def unpublish(request):
    Quizes=Quiz.objects.filter(published=False)
    context={'quizes':Quizes}
    return render(request,"Exam/unpublish.html",context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher'])
def publish(request,pk):
    quiz=Quiz.objects.filter(id=pk).update(published=True)
    messages.info(request,"Quiz is now Live")
    return redirect('home')

@login_required(login_url='login')
@allowed_users(allowed_roles=['teacher'])
def AddQnA(request,slug):
    if request.method=='POST':
        quiz_ins=Quiz.objects.get(slug=slug)
        quesform=QuestionForm(request.POST)
        ansform=[AnswerForm(request.POST,prefix=str(x)) for x in range(4)]
        if quesform.is_valid() and all([af.is_valid for af in ansform]):
            ques=quesform.save(commit=False)
            ques.quiz=quiz_ins
            ques.save()
            for af in ansform:
                new_af=af.save(commit=False)
                new_af.question=ques
                new_af.save()
            return redirect('/addqna/'+str(slug))      
    else:
        ansform=[AnswerForm(prefix=str(x)) for x in range(4)]
        quesform=QuestionForm()
    context={'ansform':ansform,'quesform':quesform}
    return render(request,"Exam/AddQnA.html",context)

@login_required(login_url='login')
def submitquizquestion(request):
    messages.info(request,"Quiz Added Successfully !!")
    return redirect('home')

@login_required(login_url='login')
def AttemptQuiz(request,slug):
    quiz=Quiz.objects.get(slug=slug)
    checkuser=QuizTakers.objects.filter(user=request.user)
    for i in checkuser:
        if(i.quiz==quiz):
            messages.warning(request,'You have already attempted the quiz !!')
            return redirect('home')
    questions=Question.objects.filter(quiz=quiz)
    questions_data=[]
    question_no=0
    for question in questions:
        dic={}
        answer=Answer.objects.filter(question=question)
        dic['question']=str(question)
        ans_dic={}
        ans_dic['a']=str(answer[0])
        ans_dic['b']=str(answer[1])
        ans_dic['c']=str(answer[2])
        ans_dic['d']=str(answer[3])
        dic['answers']=ans_dic
        if(answer[0].is_correct):
            dic['correctAnswer']='a'
        elif(answer[1].is_correct):
            dic['correctAnswer']='b'
        elif(answer[2].is_correct):
            dic['correctAnswer']='c'
        elif(answer[3].is_correct):
            dic['correctAnswer']='d'
        questions_data.append(dic)
    json_ques=json.dumps(questions_data,indent=2)
    print(quiz.time)
    context={'questions_data':json_ques,'quiz_name':quiz}
    return render(request,"Exam/AttempQuiz.html",context)

@login_required(login_url='login')
def SubmitQuiz(request):
    if request.is_ajax:
        l=eval(request.body)
        user=request.user
        quiz_name=Quiz.objects.get(name=l["Quiz"])
        checkuser=QuizTakers.objects.filter(user=request.user)
        for i in checkuser:
            if(i.quiz==quiz_name):
                messages.info(request,'You Can view Results in Profile Page !!')
            return redirect('home')
        score=int(l["Score"])
        quiztaker=QuizTakers.objects.create(
            user=user,quiz=quiz_name,correct_answers=score,
            completed=True
        )
        l.pop("Quiz")
        l.pop("Score")
        for ques,ans in l.items():
            if ans=="null":
                Response.objects.create(
                quiz=quiz_name,
                quiztaker=quiztaker,
                question=Question.objects.get(label=ques),
            )  
            else:
                question=Question.objects.get(label=ques)
                answer=Answer.objects.filter(question=question).get(text=ans)
                Response.objects.create(
                quiz=quiz_name,
                quiztaker=quiztaker,
                question=question,
                answer=answer
            )
        messages.success(request,'Test Completed Successfully !!')
        return HttpResponse("Success")
    else:
        messages.warning(request,'TEST NOT SUBMITTED !!')
        return HttpResponse("Failed")

@login_required(login_url='login')
def profile(request):
    profile=QuizTakers.objects.filter(user=request.user)
    quiz=Quiz.objects.filter(user=request.user)
    context={
        'profile':profile,"quiz":quiz,
    }
    return render(request,"Exam/Profile.html",context)

@login_required(login_url='login')
def ViewResponse(request,pk):
    quiz=Quiz.objects.get(id=pk)
    quiztaker=QuizTakers.objects.get(user=request.user,quiz=quiz)
    response = Response.objects.filter(quiztaker=quiztaker,quiz=quiz)
    context={
        "response":response,"quiz":quiz
    }
    return render(request,"Exam/Response.html",context)

@login_required(login_url='login')
def Report(request,pk):
    quiz=Quiz.objects.get(id=pk)
    quiztaker=QuizTakers.objects.get(user=request.user,quiz=quiz)
    response = Response.objects.filter(quiztaker=quiztaker,quiz=quiz)
    context={
        "response":response,"quiz":quiz
    }
    return render(request,"Exam/Report.html",context)

@login_required(login_url='login')
def sendreport(request,pk):
    quiz=Quiz.objects.get(id=pk)
    quiztaker=QuizTakers.objects.get(user=request.user,quiz=quiz)
    response = Response.objects.filter(quiztaker=quiztaker,quiz=quiz)
    subject=str(quiz)+ " Results "
    message=get_template('Exam/Report.html').render({
        "response":response,"quiz":quiz
    })
    try:
        email_from = settings.EMAIL_HOST_USER 
        msg =EmailMessage(subject,
        message,email_from,
        [request.user.email,])
        msg.content_subtype = "html" 
        msg.send()
        messages.info(request,'Report Send Successfully !!')
        return redirect('profile')
    except BadHeaderError:
        return HttpResponse('Invalid header found.')  


#AI Proctoring .......................

#AI Proctoring .......................

class VideoCamera(object):

    def __init__(self):
        print("[INFO] starting video stream...")
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def start(self):
        vid = self.video
        while(True):
            ret,img = vid.read()
            ret,frame = cv2.imencode('.jpg',img)
            return frame.tobytes()

def opencv_stream(camera,flag=1):
    while True and flag==1:
        frame=camera.start()
        yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@gzip.gzip_page
def video(request):
    try:
        return StreamingHttpResponse(opencv_stream(VideoCamera()),content_type="multipart/x-mixed-replace;boundary=frame")
    except HttpResponseServerError as e:
        print("aborted")