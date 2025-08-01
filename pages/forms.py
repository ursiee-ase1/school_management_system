from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'grade', 'date_of_birth', 'fees_due', 'fees_paid']
