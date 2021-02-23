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
            #return redirect('home')
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
        messages.info(request,'Test Completed Successfully !!')
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

def ViewResponse(request,pk):
    quiz=Quiz.objects.get(id=pk)
    quiztaker=QuizTakers.objects.get(user=request.user,quiz=quiz)
    response = Response.objects.filter(quiztaker=quiztaker,quiz=quiz)
    context={
        "response":response,"quiz":quiz
    }
    return render(request,"Exam/Response.html",context)

def Report(request,pk):
    quiz=Quiz.objects.get(id=pk)
    quiztaker=QuizTakers.objects.get(user=request.user,quiz=quiz)
    response = Response.objects.filter(quiztaker=quiztaker,quiz=quiz)
    context={
        "response":response,"quiz":quiz
    }
    return render(request,"Exam/Report.html",context)

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

def shape_to_np(shape, dtype="int"):
	# initialize the list of (x, y)-coordinates
	coords = np.zeros((68, 2), dtype=dtype)
	# loop over the 68 facial landmarks and convert them
	# to a 2-tuple of (x, y)-coordinates
	for i in range(0, 68):
		coords[i] = (shape.part(i).x, shape.part(i).y)
	# return the list of (x, y)-coordinates
	return coords

def eye_on_mask(mask, side,shape):
    points = [shape[i] for i in side]
    points = np.array(points, dtype=np.int32)
    mask = cv2.fillConvexPoly(mask, points, 255)
    return mask

def contouring(thresh, mid, img, right=False):
    cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    try:
        cnt = max(cnts, key = cv2.contourArea)
        M = cv2.moments(cnt)
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        if right:
            cx += mid
        cv2.circle(img, (cx, cy), 4, (0, 0, 255), 2)
    except:
        pass
    
def donothing(x):
    pass

class VideoCamera(object):

    def __init__(self):
        print("[INFO] starting video stream...")
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def start(self):
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor('Exam/shape_predictor_68_face_landmarks.dat')

        left = [36, 37, 38, 39, 40, 41]
        right = [42, 43, 44, 45, 46, 47]

        ret, img = self.video.read()
        thresh = img.copy()

        cv2.namedWindow('image')
        kernel = np.ones((9, 9), np.uint8)

        cv2.createTrackbar('threshold', 'eyes', 75, 255,donothing)
        while(True):
            ret,img = self.video.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            rects = detector(gray, 1)
            for rect in rects:
                shape = predictor(gray, rect)
                shape = shape_to_np(shape)
                mask = np.zeros(img.shape[:2], dtype=np.uint8)
                mask = eye_on_mask(mask, left,shape)
                mask = eye_on_mask(mask, right,shape)
                mask = cv2.dilate(mask, kernel, 5)
                eyes = cv2.bitwise_and(img, img, mask=mask)
                mask = (eyes == [0, 0, 0]).all(axis=2)
                eyes[mask] = [255, 255, 255]
                mid = (shape[42][0] + shape[39][0]) // 2
                eyes_gray = cv2.cvtColor(eyes, cv2.COLOR_BGR2GRAY)
                threshold = cv2.getTrackbarPos('threshold', 'image')
                _, thresh = cv2.threshold(eyes_gray, threshold, 255, cv2.THRESH_BINARY)
                thresh = cv2.erode(thresh, None, iterations=2) #1
                thresh = cv2.dilate(thresh, None, iterations=4) #2
                thresh = cv2.medianBlur(thresh, 3) #3
                thresh = cv2.bitwise_not(thresh)
                contouring(thresh[:, 0:mid], mid, img)
                contouring(thresh[:, mid:], mid, img, True)
                resize=cv2.resize(img, (480,320), interpolation = cv2.INTER_LINEAR)
            ret,frame = cv2.imencode('.jpg',resize)
            return frame.tobytes()

def opencv_stream(camera):
    while True:
        frame=camera.start()
        yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@gzip.gzip_page
def video(request):
    try:
        return StreamingHttpResponse(opencv_stream(VideoCamera()),content_type="multipart/x-mixed-replace;boundary=frame")
    except HttpResponseServerError as e:
        print("aborted")