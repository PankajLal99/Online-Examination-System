from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

branches=[
    ("CSE","CSE"),
    ("ME","ME"),
    ("ECE","ECE"),
    ("EX","EX"),
    ("CE","CE"),
]

sem=[
    ("I","I"),
    ("II","II"),
    ("III","III"),
    ("IV","IV"),
    ("V","V"),
    ("VI","VI"),
    ("VII","VII"),
    ("VIII","VIII"),
]

class Quiz(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=1000)
    Branch=models.CharField(max_length=20,null=True,choices=branches)
    Sem=models.CharField(max_length=20,null=True,choices=sem)
    description = models.CharField(max_length=70)
    total_marks = models.IntegerField(help_text="Enter total Marks Note:Each Question is of 1 Marks ! ")
    time=models.IntegerField(help_text="Enter total Time in Minutes ! ")
    created = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True)
    published = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created",]
        verbose_name_plural ="Quizzes"

    def __str__(self):
          return self.name

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    label = models.TextField()

    def __str__(self):
        return self.label

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=1000)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class QuizTakers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    correct_answers = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user.username

class Response(models.Model):
    quiztaker = models.ForeignKey(QuizTakers, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer,on_delete=models.CASCADE,null=True,blank=True)
    
    def __str__(self):
        return self.question.label

@receiver(pre_save, sender=Quiz)
def slugify_title(sender, instance, *args, **kwargs):
    instance.slug = slugify(instance.name)