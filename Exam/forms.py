from . import models
from django import forms

class QuizForm(forms.ModelForm):
    class Meta:
        model=models.Quiz
        fields=['name','description','total_marks','time','published']

class QuestionForm(forms.ModelForm):
    class Meta:
        model=models.Question
        fields=['label',]
        labels = {
        "label": "Question Text"
        }
        widgets={'label': forms.Textarea(attrs={
            'placeholder': 'Enter Question here'}),
        }

class AnswerForm(forms.ModelForm):
    class Meta:
        model=models.Answer
        fields=['text','is_correct']
        widgets={'text': forms.TextInput(attrs={
            'placeholder': 'Enter Answers here'}),
        }

