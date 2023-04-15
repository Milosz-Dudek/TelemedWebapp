from django.forms import ModelForm
from .models import Rehabilitator, Patient, Exercise, ExerciseData
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User


class RehabilitatorRegisterForm(ModelForm):
    name = forms.CharField(max_length=30)
    surname = forms.CharField(max_length=30)
    expertise = forms.CharField(max_length=50)
    sex = forms.ChoiceField(choices=(('M', 'Male'), ('F', 'Female')), widget=forms.RadioSelect)
    location = forms.CharField(max_length=30)
    street = forms.CharField(max_length=50)
    house_number = forms.CharField(max_length=10)
    local_number = forms.CharField(required=False)
    entity_name = forms.CharField(max_length=50)

    class Meta:
        model = Rehabilitator
        fields = ['name', 'surname', 'expertise', 'sex', 'location', 'street', 'house_number', 'local_number',
                  'entity_name']

    def clean_email(self):
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')

        if email and User.objects.filter(email=email).exclude(username=username).count():
            raise forms.ValidationError(
                'This email address is already in use. Please supply a different email address.')
        return email


class PatientRegisterForm(ModelForm):
    name = forms.CharField(max_length=30)
    surname = forms.CharField(max_length=30)
    sex = forms.ChoiceField(choices=(('M', 'Male'), ('F', 'Female')), widget=forms.RadioSelect)
    birth_date = forms.DateTimeField()
    location = forms.CharField(max_length=30)
    street = forms.CharField(max_length=50)
    house_number = forms.CharField(max_length=10)
    local_number = forms.CharField(required=False)
    rehabilitator = forms.ModelChoiceField(queryset=Rehabilitator.objects.all(), required=False,
                                           widget=forms.Select(attrs={'class': 'selectpicker'}))

    class Meta:
        model = Patient
        fields = ['name', 'surname', 'sex', 'birth_date', 'location', 'street', 'house_number', 'local_number', 'rehabilitator']

    def clean_email(self):
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')

        if email and User.objects.filter(email=email).exclude(username=username).count():
            raise forms.ValidationError(
                'This email address is already in use. Please supply a different email address.')
        return email


class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']


class ExerciseForm(ModelForm):
    type_of_exercise = forms.ChoiceField(choices=(('Sit-ups', 'Sit-ups'), ('Jumping-jacks', 'Jumping-jacks')),
                                         widget=forms.RadioSelect)
    date_of_exercise = forms.DateTimeField()

    class Meta:
        model = Exercise
        fields = ['type_of_exercise', 'date_of_exercise']
        exclude = ['patient']


class ExerciseDataForm(ModelForm):
    exercise_data_file = forms.FileField()

    class Meta:
        model = ExerciseData
        fields = ['time', 'seconds_elapsed', 'z', 'y', 'z']
        exclude = ['exercise']
