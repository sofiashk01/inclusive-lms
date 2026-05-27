from django import forms
from .models import LabSubmission, Course


class LabSubmissionForm(forms.ModelForm):


    class Meta:
        model = LabSubmission
        fields = ['course', 'lab_title', 'file']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course'].widget.attrs.update({
            'class': 'form-select',
            'aria-label': 'Оберіть курс'
        })
        self.fields['lab_title'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Наприклад: Лабораторна робота №1'
        })
        self.fields['file'].widget.attrs.update({
            'class': 'form-control'
        })