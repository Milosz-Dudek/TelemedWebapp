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


class PatientRegisterForm(ModelForm):
    name = forms.CharField(max_length=30)
    surname = forms.CharField(max_length=30)
    sex = forms.ChoiceField(choices=(('M', 'Male'), ('F', 'Female')), widget=forms.RadioSelect)
    birth_date = forms.DateTimeField(widget=forms.TextInput(attrs={'class': 'form-control', 'type':'date'}))
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


# class PatientFilterForm(forms.Form):
#     name = forms.CharField(required=False)
#     surname = forms.CharField(required=False)
#     sex = forms.ChoiceField(choices=[('', 'Any'), ('M', 'Male'), ('F', 'Female')], required=False)
#
#     def filter_queryset(self, queryset):
#         name = self.cleaned_data['name']
#         surname = self.cleaned_data['surname']
#         sex = self.cleaned_data['sex']
#
#         if name:
#             queryset = queryset.filter(name__icontains=name)
#         if surname:
#             queryset = queryset.filter(surname__icontains=surname)
#         if sex:
#             queryset = queryset.filter(sex=sex)
#
#         return queryset.order_by('surname', 'name')

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        surname = cleaned_data.get('surname')
        sex = cleaned_data.get('sex')

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




