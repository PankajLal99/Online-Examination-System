from django.contrib.auth.models import User
from django.db import models
#for reciver 
from django.db.models.signals import post_save
from django.dispatch import receiver
#end reciver

branches=[
    ("CSE","CSE"),
    ("ME","ME"),
]

sem=[
    ("I","I"),
    ("II","II"),
    ("III","III"),
    ("IV","IV"),
]
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    Sem=models.CharField(max_length=20,null=True,choices=sem)
    Branch=models.CharField(max_length=20,null=True,choices=branches)
    RollNo=models.CharField(max_length=20,unique=True,blank=True,null=True)
    signup_confirmation = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.user)

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    Branch=models.CharField(max_length=20,null=True,choices=branches)
    Sem=models.CharField(max_length=20,null=True,choices=sem)
    UID=models.CharField(max_length=20,unique=True,blank=True,null=True)
    signup_confirmation = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.user)

@receiver(post_save, sender=User)
def update_student_signal(sender, instance, created, **kwargs):
    if created:
        Student.objects.create(user=instance)
    instance.student.save()
    
@receiver(post_save, sender=User)
def update_teacher_signal(sender, instance, created, **kwargs):
    if created:
        Teacher.objects.create(user=instance)
    instance.teacher.save()