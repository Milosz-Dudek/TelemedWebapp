import csv
import io

from django.db import transaction
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


class RehabilitatorFilterForm(forms.Form):
    name = forms.CharField(label='name', required=False)
    surname = forms.CharField(label='surname', required=False)
    expertise = forms.CharField(label='expertise', required=False)
    location = forms.CharField(label='location', required=False)
    entity_name = forms.CharField(label='entity_name', required=False)


class PatientRegisterForm(ModelForm):
    name = forms.CharField(max_length=30)
    surname = forms.CharField(max_length=30)
    sex = forms.ChoiceField(choices=(('M', 'Male'), ('F', 'Female')), widget=forms.RadioSelect)
    birth_date = forms.DateTimeField(widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'date'}))
    location = forms.CharField(max_length=30)
    street = forms.CharField(max_length=50)
    house_number = forms.CharField(max_length=10)
    local_number = forms.CharField(required=False)
    rehabilitator = forms.ModelChoiceField(queryset=Rehabilitator.objects.all(), required=False,
                                           widget=forms.Select(attrs={'class': 'selectpicker'}))

    class Meta:
        model = Patient
        fields = ['name', 'surname', 'sex', 'birth_date', 'location', 'street',
                  'house_number', 'local_number', 'rehabilitator']

    def clean_email(self):
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')

        if email and User.objects.filter(email=email).exclude(username=username).count():
            raise forms.ValidationError(
                'This email address is already in use. Please supply a different email address.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        surname = cleaned_data.get('surname')
        sex = cleaned_data.get('sex')


class PatientFilterForm(forms.Form):
    name = forms.CharField(label='name', required=False)
    surname = forms.CharField(label='surname', required=False)
    sex = forms.ChoiceField(label='sex', choices=[('', 'Any'), ('M', 'Male'), ('F', 'Female')], required=False)
    birth_date_from = forms.DateTimeField(label='birth_date_from',
                                          widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'date'}),
                                          required=False)
    birth_date_till = forms.DateTimeField(label='birth_date_till',
                                          widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'date'}),
                                          required=False)


class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']


class ExerciseForm(ModelForm):
    type_of_exercise = forms.ChoiceField(choices=(('Sit-ups', 'Sit-ups'), ('Jumping-jacks', 'Jumping-jacks')),
                                         widget=forms.RadioSelect)
    date_of_exercise = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
    )

    class Meta:
        model = Exercise
        fields = ['type_of_exercise', 'date_of_exercise']
        exclude = ['patient']


class ExerciseFilterForm(forms.Form):
    type_of_exercise = forms.ChoiceField(label='type_of_exercise',
                                         choices=(('Sit-ups', 'Sit-ups'), ('Jumping-jacks', 'Jumping-jacks')),
                                         widget=forms.RadioSelect, required=False)
    date_of_exercise_from = forms.DateTimeField(label="date_of_exercise",
                                                widget=forms.DateTimeInput(
                                                    attrs={'class': 'form-control', 'type': 'datetime-local'}),
                                                required=False
                                                )
    date_of_exercise_till = forms.DateTimeField(label="date_of_exercise",
                                                widget=forms.DateTimeInput(
                                                    attrs={'class': 'form-control', 'type': 'datetime-local'}),
                                                required=False
                                                )


class ExerciseDataForm(ModelForm):
    csv_file = forms.FileField()

    class Meta:
        model = ExerciseData
        fields = ('csv_file',)

    @transaction.atomic
    def save(self, commit=True, exercise=None):
        csv_file = self.cleaned_data.get('csv_file')
        if csv_file:
            # process the csv file and save the exercise data
            reader = csv.DictReader(io.StringIO(csv_file.read().decode('utf-8')))
            exercise_data_list = []
            for row in reader:
                exercise_data = ExerciseData(exercise=exercise,
                                             time=row['time'],
                                             seconds_elapsed=row['seconds_elapsed'],
                                             z=row['z'],
                                             y=row['y'],
                                             x=row['x'])
                exercise_data_list.append(exercise_data)

            # Use bulk_create to create ExerciseData instances in bulk
            ExerciseData.objects.bulk_create(exercise_data_list)

            if commit:
                exercise.save()

        else:
            raise ValueError('No CSV file provided')

        return exercise
