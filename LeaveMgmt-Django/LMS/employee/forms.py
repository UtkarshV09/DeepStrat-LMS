from django import forms
from employee.models import Role, Department, Employee
from django.contrib.auth.models import User


# EMPLoYEE
class EmployeeCreateForm(forms.ModelForm):
    image = forms.ImageField(
        widget=forms.FileInput(attrs={'onchange': 'previewImage(this);'})
    )

    class Meta:
        model = Employee
        exclude = [
            'is_blocked',
            'is_deleted',
            'created',
            'updated',
            'employeeid',
            'dateissued',
        ]
        widgets = {'bio': forms.Textarea(attrs={'cols': 5, 'rows': 5})}
