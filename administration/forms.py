from django.contrib.auth.forms import UserCreationForm
from administration.models import User,Employee, Group
from django.db import transaction
from django import forms




class ManagerSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_manager = True
        if commit:
            user.save()
        return user



class EmployeeSignupForm(UserCreationForm):
    fullName=forms.CharField(max_length=150)
    choice=[
        (1,"ACC"),
        (2,"APP"),
        (3,"ACC supervisor"),
        (4,"APP supervisor"),
        (5,"Tower supervisor"),
    ]
    Level = forms.ChoiceField(
        choices=choice
    )
    age=forms.IntegerField()
    phoneNumber = forms.CharField(max_length=100)
    group = forms.ModelChoiceField(
        queryset=Group.objects.filter(),
        empty_label="----------",
        required=True,
        initial=None,
        label=None
    )
    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic()
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_empolyee = True
        user.save()
        employee = Employee.objects.create(
            user=user,
            level=self.cleaned_data.get('Level'),
            group=self.cleaned_data.get('group'),
            age=self.cleaned_data.get('age'),
            fullName=self.cleaned_data.get('fullName'),
            phoneNumber = self.cleaned_data.get('phoneNumber')
        )
        return user

